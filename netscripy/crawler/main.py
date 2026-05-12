import os
import sys
import random
import time
import logging
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mongodb_connection import MongoDBConnection
from data_models import (
    create_project_doc,
    create_owner_doc,
    create_organization_doc,
    create_commit_doc,
    create_contributor_doc
)
from github_crawler import GitHubCrawler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("crawler.log"), logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class GitHubDataPipeline:
    def __init__(self, github_token=None):
        self.mongo = MongoDBConnection(host='localhost', port=27017, db_name='github_analysis')
        self.crawler = GitHubCrawler(token=github_token)
        self.running = True
        self.crawl_count = 0
        self.total_projects = 0
        self.total_commits = 0
        self.total_contributors = 0
    
    def initialize(self):
        logger.info("初始化MongoDB数据库...")
        if not self.mongo.initialize_database():
            logger.error("MongoDB初始化失败")
            return False
        logger.info("MongoDB数据库初始化成功")
        return True
    
    def process_owner(self, owner_data):
        existing = self.mongo.find_one("owners", {"login": owner_data.get("login")})
        if existing:
            logger.debug(f"所有者已存在: {owner_data.get('login')}")
            return existing["_id"]
        
        owner_doc = create_owner_doc(owner_data)
        owner_id = self.mongo.insert_one("owners", owner_doc)
        logger.info(f"插入新所有者: {owner_data.get('login')}")
        return owner_id
    
    def process_organization(self, org_data):
        existing = self.mongo.find_one("organizations", {"login": org_data.get("login")})
        if existing:
            logger.debug(f"组织已存在: {org_data.get('login')}")
            return existing["_id"]
        
        org_doc = create_organization_doc(org_data)
        org_id = self.mongo.insert_one("organizations", org_doc)
        logger.info(f"插入新组织: {org_data.get('login')}")
        return org_id
    
    def process_project(self, repo_data):
        full_name = repo_data.get("full_name")
        existing = self.mongo.find_one("projects", {"full_name": full_name})
        if existing:
            logger.debug(f"项目已存在: {full_name}")
            return existing["_id"], False
        
        owner_data = repo_data.get("owner", {})
        owner_id = None
        
        if owner_data.get("type") == "Organization":
            org_id = self.process_organization(owner_data)
            owner_id = org_id
        else:
            owner_id = self.process_owner(owner_data)
        
        project_doc = create_project_doc(repo_data, owner_id)
        project_id = self.mongo.insert_one("projects", project_doc)
        logger.info(f"插入新项目: {full_name}")
        self.total_projects += 1
        
        return project_id, True
    
    def process_commits(self, project_id, owner, repo):
        logger.info(f"开始爬取提交记录: {owner}/{repo}")
        commits = self.crawler.get_repo_commits(owner, repo, per_page=30, max_pages=3)
        
        commit_docs = []
        for commit in commits:
            commit_doc = create_commit_doc(project_id, commit)
            commit_docs.append(commit_doc)
        
        if commit_docs:
            self.mongo.insert_many("commits", commit_docs)
            self.total_commits += len(commit_docs)
            logger.info(f"插入 {len(commit_docs)} 条提交记录")
    
    def process_contributors(self, project_id, owner, repo):
        logger.info(f"开始爬取贡献者: {owner}/{repo}")
        contributors = self.crawler.get_repo_contributors(owner, repo, per_page=30, max_pages=2)
        
        contributor_docs = []
        for contributor in contributors:
            contributor_doc = create_contributor_doc(project_id, contributor)
            contributor_docs.append(contributor_doc)
        
        if contributor_docs:
            self.mongo.insert_many("contributors", contributor_docs)
            self.total_contributors += len(contributor_docs)
            logger.info(f"插入 {len(contributor_docs)} 条贡献者记录")
    
    def crawl_batch(self, languages=None, batch_size=20, include_commits=True, include_contributors=True):
        logger.info(f"=== 开始第 {self.crawl_count + 1} 轮爬取 ===")
        
        try:
            projects = self.crawler.search_top_projects(languages=languages, stars_min=5000, max_results=batch_size)
            
            if not projects:
                logger.warning("本轮未获取到任何项目数据")
                return
            
            for i, repo in enumerate(projects, 1):
                if not self.running:
                    logger.info("检测到停止信号，退出爬取")
                    break
                
                logger.info(f"处理项目 {i}/{len(projects)}: {repo.get('full_name')}")
                
                project_id, is_new = self.process_project(repo)
                
                if project_id and is_new and include_commits:
                    full_name = repo.get("full_name", "")
                    if "/" in full_name:
                        owner, name = full_name.split("/", 1)
                        self.process_commits(project_id, owner, name)
                        time.sleep(random.uniform(0.5, 1.0))
                
                if project_id and is_new and include_contributors:
                    full_name = repo.get("full_name", "")
                    if "/" in full_name:
                        owner, name = full_name.split("/", 1)
                        self.process_contributors(project_id, owner, name)
                        time.sleep(random.uniform(0.5, 1.0))
                
                time.sleep(random.uniform(1.0, 2.0))
            
            self.crawl_count += 1
            logger.info(f"=== 第 {self.crawl_count} 轮爬取完成 ===")
            
        except Exception as e:
            logger.error(f"爬取过程中发生错误: {e}", exc_info=True)
    
    def continuous_crawl(self, languages=None, batch_size=20, interval_minutes=60, include_commits=True, include_contributors=True):
        logger.info("=== 启动持续爬取模式 ===")
        logger.info(f"爬取间隔: {interval_minutes} 分钟")
        logger.info(f"每轮爬取项目数: {batch_size}")
        logger.info("按 Ctrl+C 停止爬取")
        
        while self.running:
            self.crawl_batch(languages=languages, batch_size=batch_size, 
                           include_commits=include_commits, 
                           include_contributors=include_contributors)
            
            if not self.running:
                break
            
            self.print_stats()
            
            logger.info(f"等待 {interval_minutes} 分钟后进行下一轮爬取...")
            for i in range(interval_minutes * 60):
                if not self.running:
                    break
                time.sleep(1)
    
    def print_stats(self):
        logger.info(f"=== 爬取统计 ===")
        logger.info(f"已完成轮数: {self.crawl_count}")
        logger.info(f"总项目数: {self.total_projects}")
        logger.info(f"总提交记录数: {self.total_commits}")
        logger.info(f"总贡献者数: {self.total_contributors}")
        
        projects_in_db = self.mongo.db.projects.count_documents({})
        owners_in_db = self.mongo.db.owners.count_documents({})
        orgs_in_db = self.mongo.db.organizations.count_documents({})
        commits_in_db = self.mongo.db.commits.count_documents({})
        contributors_in_db = self.mongo.db.contributors.count_documents({})
        
        logger.info(f"=== 数据库统计 ===")
        logger.info(f"项目数: {projects_in_db}")
        logger.info(f"所有者数: {owners_in_db}")
        logger.info(f"组织数: {orgs_in_db}")
        logger.info(f"提交记录数: {commits_in_db}")
        logger.info(f"贡献者数: {contributors_in_db}")
    
    def stop(self):
        self.running = False
        logger.info("收到停止信号，正在停止爬取...")
    
    def close(self):
        self.mongo.close()

if __name__ == "__main__":
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    
    pipeline = GitHubDataPipeline(github_token=GITHUB_TOKEN)
    
    if not pipeline.initialize():
        sys.exit(1)
    
    try:
        languages = ["Python", "JavaScript", "Java", "TypeScript", "Go", "Rust", "C++", "Ruby", "PHP", "Swift"]
        
        pipeline.continuous_crawl(
            languages=languages,
            batch_size=20,
            interval_minutes=60,
            include_commits=True,
            include_contributors=True
        )
    
    except KeyboardInterrupt:
        logger.info("收到 Ctrl+C 信号")
        pipeline.stop()
    
    except Exception as e:
        logger.error(f"程序异常退出: {e}", exc_info=True)
    
    finally:
        pipeline.print_stats()
        pipeline.close()
        logger.info("爬虫已停止")