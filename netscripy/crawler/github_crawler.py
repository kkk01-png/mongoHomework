import requests
import time
import random
from datetime import datetime, timedelta

class GitHubCrawler:
    def __init__(self, token=None, rate_limit_wait=True):
        self.token = token
        self.rate_limit_wait = rate_limit_wait
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Analysis-Crawler"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        self.last_request_time = datetime.now()
        self.min_request_interval = 1.0

    def _rate_limit_sleep(self):
        current_time = datetime.now()
        time_diff = (current_time - self.last_request_time).total_seconds()
        if time_diff < self.min_request_interval:
            time.sleep(self.min_request_interval - time_diff)
        self.last_request_time = datetime.now()

    def _make_request(self, url, params=None):
        self._rate_limit_sleep()
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 403:
                if self.rate_limit_wait:
                    reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
                    wait_time = max(reset_time - time.time(), 0) + 10
                    print(f"API速率限制，等待 {wait_time:.2f} 秒...")
                    time.sleep(wait_time)
                    return self._make_request(url, params)
                else:
                    raise Exception("API速率限制")
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def search_repositories(self, query, per_page=30, max_pages=10):
        results = []
        page = 1
        
        while page <= max_pages:
            params = {
                "q": query,
                "per_page": per_page,
                "page": page,
                "sort": "stars",
                "order": "desc"
            }
            
            url = f"{self.base_url}/search/repositories"
            data = self._make_request(url, params)
            
            if not data or "items" not in data:
                break
            
            results.extend(data["items"])
            page += 1
            
            if len(data["items"]) < per_page:
                break
            
            time.sleep(random.uniform(0.5, 1.5))
        
        return results

    def get_repository(self, owner, repo):
        url = f"{self.base_url}/repos/{owner}/{repo}"
        return self._make_request(url)

    def get_repo_commits(self, owner, repo, per_page=30, max_pages=5):
        results = []
        page = 1
        
        while page <= max_pages:
            params = {
                "per_page": per_page,
                "page": page
            }
            
            url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            data = self._make_request(url, params)
            
            if not data:
                break
            
            results.extend(data)
            
            if len(data) < per_page:
                break
            
            page += 1
            time.sleep(random.uniform(0.3, 0.8))
        
        return results

    def get_repo_contributors(self, owner, repo, per_page=30, max_pages=3):
        results = []
        page = 1
        
        while page <= max_pages:
            params = {
                "per_page": per_page,
                "page": page
            }
            
            url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
            data = self._make_request(url, params)
            
            if not data:
                break
            
            results.extend(data)
            
            if len(data) < per_page:
                break
            
            page += 1
            time.sleep(random.uniform(0.3, 0.8))
        
        return results

    def get_organization(self, org_name):
        url = f"{self.base_url}/orgs/{org_name}"
        return self._make_request(url)

    def get_org_repositories(self, org_name, per_page=30, max_pages=5):
        results = []
        page = 1
        
        while page <= max_pages:
            params = {
                "per_page": per_page,
                "page": page,
                "sort": "updated"
            }
            
            url = f"{self.base_url}/orgs/{org_name}/repos"
            data = self._make_request(url, params)
            
            if not data:
                break
            
            results.extend(data)
            
            if len(data) < per_page:
                break
            
            page += 1
            time.sleep(random.uniform(0.3, 0.8))
        
        return results

    def get_user(self, username):
        url = f"{self.base_url}/users/{username}"
        return self._make_request(url)

    def get_rate_limit(self):
        url = f"{self.base_url}/rate_limit"
        return self._make_request(url)

    def search_top_projects(self, languages=None, stars_min=1000, max_results=100):
        results = []
        
        if not languages:
            languages = ["Python", "JavaScript", "Java", "TypeScript", "Go", "Rust", "C++", "Ruby", "PHP", "Swift"]
        
        for language in languages:
            query = f"language:{language} stars:>{stars_min}"
            repos = self.search_repositories(query, per_page=30, max_pages=(max_results // 30) + 1)
            
            for repo in repos[:max_results // len(languages)]:
                full_name = repo.get("full_name", "")
                if full_name and "/" in full_name:
                    owner, name = full_name.split("/", 1)
                    full_data = self.get_repository(owner, name)
                    if full_data:
                        results.append(full_data)
                
                if len(results) >= max_results:
                    break
            
            if len(results) >= max_results:
                break
        
        return results