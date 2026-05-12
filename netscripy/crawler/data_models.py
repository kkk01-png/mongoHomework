from datetime import datetime

def create_project_doc(github_data, owner_id=None):
    return {
        "name": github_data.get("name"),
        "full_name": github_data.get("full_name"),
        "owner": owner_id,
        "description": github_data.get("description"),
        "language": github_data.get("language"),
        "stars_count": github_data.get("stargazers_count", 0),
        "forks_count": github_data.get("forks_count", 0),
        "open_issues_count": github_data.get("open_issues_count", 0),
        "created_at": datetime.strptime(github_data.get("created_at"), "%Y-%m-%dT%H:%M:%SZ") if github_data.get("created_at") else None,
        "updated_at": datetime.strptime(github_data.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ") if github_data.get("updated_at") else None,
        "topics": github_data.get("topics", []),
        "license": github_data.get("license", {}).get("key") if github_data.get("license") else None,
        "watchers_count": github_data.get("watchers_count", 0),
        "size": github_data.get("size", 0),
        "default_branch": github_data.get("default_branch", "main"),
        "category": None,
        "quality_score": None,
        "long_term_value": None
    }

def create_owner_doc(owner_data):
    return {
        "login": owner_data.get("login"),
        "type": owner_data.get("type"),
        "avatar_url": owner_data.get("avatar_url"),
        "url": owner_data.get("html_url"),
        "repos_count": None,
        "followers_count": None
    }

def create_organization_doc(org_data):
    return {
        "login": org_data.get("login"),
        "name": org_data.get("name"),
        "description": org_data.get("description"),
        "avatar_url": org_data.get("avatar_url"),
        "url": org_data.get("html_url"),
        "repos_count": org_data.get("public_repos", 0),
        "members_count": None,
        "created_at": datetime.strptime(org_data.get("created_at"), "%Y-%m-%dT%H:%M:%SZ") if org_data.get("created_at") else None,
        "activity_score": None,
        "tech_depth": None,
        "main_tech_stacks": []
    }

def create_commit_doc(project_id, commit_data):
    commit_author = commit_data.get("commit", {}).get("author", {})
    return {
        "project_id": project_id,
        "sha": commit_data.get("sha"),
        "author": commit_data.get("author", {}).get("login") if commit_data.get("author") else commit_author.get("name"),
        "message": commit_data.get("commit", {}).get("message", ""),
        "date": datetime.strptime(commit_author.get("date"), "%Y-%m-%dT%H:%M:%SZ") if commit_author.get("date") else None,
        "additions": commit_data.get("stats", {}).get("additions", 0),
        "deletions": commit_data.get("stats", {}).get("deletions", 0)
    }

def create_contributor_doc(project_id, contributor_data):
    return {
        "login": contributor_data.get("login"),
        "avatar_url": contributor_data.get("avatar_url"),
        "contributions": contributor_data.get("contributions", 0),
        "project_id": project_id
    }

def create_analysis_result_doc(analysis_type, analysis_data, period="monthly", accuracy=0.0):
    return {
        "analysis_type": analysis_type,
        "analysis_data": analysis_data,
        "period": period,
        "created_at": datetime.now(),
        "accuracy": accuracy
    }

def create_search_record_doc(query, query_type, results, match_score=0.0, validated=False, validation_result=None):
    return {
        "query": query,
        "query_type": query_type,
        "results": results,
        "match_score": match_score,
        "validated": validated,
        "validation_result": validation_result,
        "created_at": datetime.now()
    }