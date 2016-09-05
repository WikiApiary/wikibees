

# Get range aggregates
select
    count(*) as stats_count,
    min(users) as min_users,
    max(users) as max_users,
    min(activeusers) as min_activeusers,
    max(activeusers) as max_activeusers,
    min(admins) as min_admins,
    max(admins) as max_admins,
    min(articles) as min_articles,
    max(articles) as max_articles,
    min(edits) as min_edits,
    max(edits) as max_edits,
    max(jobs) as max_jobs,
    min(pages) as min_pages,
    max(pages) as max_pages,
    min(views) as min_views,
    max(views) as max_views
from
    statistics
where
    website_id = 18 and
    capture_date > '2013-05-18 00:00:00'
    and capture_date < '2013-05-18 23:59:59';

# Get first values

# Get last values
