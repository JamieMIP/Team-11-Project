# Team-11-Project
# Forums and Knowledge Base

**COB290 Group Project, Team 11. Productivity and knowledge management system, Part 1 prototype.**

**Author:** Dominic Stachura · **Team:** Team 11 · **Status:** in progress

This README covers the design of the **Posts** section. The algorithm-ranked posts feed is the **default home page** of the app, so it's the first thing every user sees.

Employees share technical knowledge (configs, bugs, fixes) and non-technical knowledge (admin processes) as **Posts** inside **Topics** such as *Software Development* or *Printing*. The feed ranks posts by relevance to the user, how recent they are and how much discussion they have. From the feed, users can create posts, open and comment on them, search, or browse a single topic.

## Tech stack

- **Language:** Python
- **GUI:** PySide6
- **Editor:** VS Code
- **Data:** dummy data only for Part 1 (no live database or login)

In VS Code, select the `.venv` interpreter with **Python: Select Interpreter** from the Command Palette.

## Progress so far

| Item | Status |
|---|---|
| Flow diagram: feed generation | Done |
| Flow diagram: user actions from the feed | Done |
| Class diagram | Done |
| Pseudocode for feed, posting, moderation and search | Done |
| Dummy data (users, teams, topics, posts, comments) | To do |
| PySide6 screens: feed, post view, create post, search, topic view | To do |
| Link the feed home page into the team's navigation | To do |

---

## Diagram 1: Posts feed generation

If a user doesn't follow any topics yet, the feed falls back to recent and popular posts so the home page is never empty.

```mermaid
flowchart TD
    A(["User opens the app"]) --> B["Load user context<br/>(role, teams, followed topics)"]
    B --> C{"Follows any topics?"}
    C -- Yes --> D["Gather posts from followed<br/>and team topics"]
    C -- No --> E["Gather recent and popular<br/>posts company-wide"]
    D --> F["Score each post<br/>(topic match, recency, activity)"]
    E --> F
    F --> G["Sort by score,<br/>newest first on ties"]
    G --> H(["Display posts feed as home page"])
```

## Diagram 2: User actions from the feed

From the feed the user can take one of four paths. Every path ends back at a feed.
- Create post: pick a topic, write the post, validate and publish.
- Open post: read the post, comment on it, or delete it if they have permission.
- Search: enter keywords and filters, then open a result. This goes to the same post view as opening a post from the feed.
- Browse topic: show the feed filtered to a single topic, ranked with the same scoring.

```mermaid
flowchart TD
    S(["Posts feed displayed"]) --> ACT{"User action?"}

    ACT -- Create post --> C1["Select topic"]
    C1 --> C2["Write title, body,<br/>links and tags"]
    C2 --> CV{"Post valid?"}
    CV -- No --> CE["Show error message"]
    CE --> C2
    CV -- Yes --> C3["Save post with author name"]
    C3 --> CR(["Return to posts feed"])

    ACT -- Open post --> O1["Show post and comments"]
    O1 --> OD{"Action on post?"}
    OD -- Back --> OB(["Return to posts feed"])
    OD -- Comment --> OC["Add comment"]
    OC --> O1
    OD -- Delete --> OM{"Author or moderator?"}
    OM -- No --> OE["Show permission message"]
    OE --> OD
    OM -- Yes --> OR["Remove post"]
    OR --> OEND(["Return to posts feed"])

    ACT -- Search --> S1["Enter keywords and filters"]
    S1 --> S2["Run search"]
    S2 --> SV{"Results found?"}
    SV -- No --> SE["Show empty state"]
    SE --> S1
    SV -- Yes --> S3["Show results list"]
    S3 --> S4["Select a result"]
    S4 --> O1

    ACT -- Browse topic --> T1["Choose a topic"]
    T1 --> T2["Filter feed to that topic"]
    T2 --> T3["Rank topic posts<br/>with same scoring"]
    T3 --> T4(["Topic feed displayed"])
```

## Diagram 3: Class diagram
Diagram 3: Class diagram

The classes fall into three layers:

- People and permissions: User, Team, Role, Permission
- Knowledge base: Topic, Post, Comment, TopicCategory
- Logic and data: FeedRanker, SearchService, SearchFilter, PostRepository

```mermaid
classDiagram
    direction TB

    class Role {
        <<enumeration>>
        EMPLOYEE
        TEAM_LEADER
        MANAGER
    }

    class Permission {
        <<enumeration>>
        MODERATE_POSTS
        CREATE_TOPICS
    }

    class TopicCategory {
        <<enumeration>>
        TECHNICAL
        NON_TECHNICAL
    }

    class User {
        -user_id: int
        -name: str
        -email: str
        -role: Role
        -extra_permissions: set~Permission~
        -followed_topics: list~Topic~
        +follow_topic(topic: Topic) None
        +unfollow_topic(topic: Topic) None
        +has_permission(p: Permission) bool
        +can_moderate() bool
    }

    class Team {
        -team_id: int
        -name: str
        -leader: User
        -members: list~User~
        -topics: list~Topic~
        +add_member(user: User) None
        +get_topics() list~Topic~
    }

    class Topic {
        -topic_id: int
        -name: str
        -description: str
        -category: TopicCategory
        -created_by: User
        +get_posts() list~Post~
    }

    class Post {
        -post_id: int
        -title: str
        -body: str
        -author: User
        -topic: Topic
        -tags: list~str~
        -created_at: datetime
        -comments: list~Comment~
        -accepted_solution: Optional~Comment~
        -is_removed: bool
        +add_comment(author: User, body: str) Comment
        +mark_solution(comment: Comment, user: User) None
        +remove(user: User) bool
        +is_solved() bool
        +last_activity() datetime
    }

    class Comment {
        -comment_id: int
        -author: User
        -body: str
        -created_at: datetime
    }

    class FeedRanker {
        -repository: PostRepository
        -FOLLOWED_WEIGHT: float = 3.0
        -TEAM_WEIGHT: float = 2.0
        -ACTIVITY_WEIGHT: float = 0.5
        -RECENCY_HALF_LIFE_DAYS: float = 3.0
        -UNSOLVED_BOOST: float = 1.0
        +build_feed(user: User, limit: int) list~Post~
        -gather_candidates(user: User) list~Post~
        -score(post: Post, user: User) float
    }

    class SearchService {
        -repository: PostRepository
        +search(keywords: str, filters: SearchFilter) list~Post~
        -matches(post: Post, keywords: str) bool
    }

    class SearchFilter {
        -topic: Optional~Topic~
        -author: Optional~User~
        -tags: list~str~
        -date_from: Optional~date~
        -date_to: Optional~date~
        -solved_only: bool
    }

    class PostRepository {
        -posts: list~Post~
        -topics: list~Topic~
        +get_all_posts() list~Post~
        +get_post(post_id: int) Post
        +add_post(post: Post) None
        +get_topics() list~Topic~
    }

    User --> "1" Role
    User --> "0..*" Permission : extra permissions
    Team "0..*" -- "1..*" User : members
    Team "0..*" -- "1" User : led by
    User "1" -- "0..*" Post : writes
    User "1" -- "0..*" Comment : writes
    User "0..*" -- "0..*" Topic : follows
    Team "0..*" -- "0..*" Topic : team topics
    Topic "1" o-- "0..*" Post : contains
    Topic --> "1" TopicCategory
    Post "1" *-- "0..*" Comment : comments
    Post --> "0..1" Comment : accepted solution
    PostRepository "1" o-- "0..*" Post
    PostRepository "1" o-- "0..*" Topic
    FeedRanker --> "1" PostRepository
    SearchService --> "1" PostRepository
    SearchService ..> SearchFilter : uses
```

---

## Design decisions

- **Moderation:** Managers can moderate by default, and anyone else can be given the `MODERATE_POSTS` permission individually. Authors can always delete their own posts.
- **Soft delete:** removing a post sets `is_removed = True` instead of deleting it, so it can still be audited.
- **Cold-start fallback:** users who follow no topics see recent and popular posts instead of an empty feed.
- **Ranking uses last activity:** an old post that gets a new comment moves back up the feed.
- **Unsolved boost:** open technical questions are pushed up so they get answered faster.

---

## Pseudocode

### Building the feed

```
FUNCTION build_feed(user, limit):
    candidates = gather_candidates(user)
    SORT candidates BY score(post, user) DESCENDING, THEN BY last_activity DESCENDING
    RETURN first <limit> posts


FUNCTION gather_candidates(user):
    all_posts = every post WHERE is_removed IS FALSE

    IF user.followed_topics IS EMPTY:
        RETURN posts in all_posts active within the last 14 days

    relevant_topics = user.followed_topics + topics of the user's teams
    RETURN posts in all_posts whose topic IS IN relevant_topics
```

### Scoring a post

The whole score is multiplied by a freshness value that halves every 3 days, so old posts sink unless someone comments again.

```
FUNCTION score(post, user):
    IF post.topic IN user.followed_topics:    topic_score = 3.0
    ELSE IF post.topic IN user's team topics: topic_score = 2.0
    ELSE:                                     topic_score = 0

    activity_score = 0.5 * log(1 + number of comments)

    IF post is TECHNICAL AND NOT post.is_solved():  unsolved_score = 1.0
    ELSE:                                           unsolved_score = 0

    age_in_days = (now - post.last_activity()) in days
    freshness = 0.5 ^ (age_in_days / 3)

    RETURN (1 + topic_score + activity_score + unsolved_score) * freshness
```

### Creating a post

```
FUNCTION create_post(user, topic, title, body, tags):
    IF topic, title or body IS BLANK:
        SHOW error message
        RETURN nothing

    post = NEW Post(title, body, topic, tags, author = user, created_at = now)
    repository.add_post(post)
    RETURN post
```

### Deleting and moderating

```
FUNCTION can_moderate(user):
    RETURN user.role IS MANAGER OR MODERATE_POSTS IN user.extra_permissions

FUNCTION remove(post, user):
    IF user IS post.author OR can_moderate(user):
        post.is_removed = TRUE
        RETURN TRUE
    SHOW permission message
    RETURN FALSE
```

### Searching

```
FUNCTION search(keywords, filters):
    words = lowercase(keywords) split on spaces
    results = empty list

    FOR EACH post NOT removed:
        IF post fails any filter (topic, author, tags, dates, solved only): SKIP

        hits = 0
        FOR EACH word IN words:
            IF word IN post.title: hits += 2     # title matches count double
            IF word IN post.body:  hits += 1
            IF word IN post.tags:  hits += 1

        IF words IS EMPTY OR hits > 0: ADD (hits, post) TO results

    SORT results BY hits DESCENDING, THEN BY newest
    RETURN posts from results
```

---

## Ideas to make the section stand out

**Recommended**

- **"Why am I seeing this?" labels:** each feed post shows its biggest scoring reason, such as *From a topic you follow* or *Unsolved in Printing*.
- **Similar post detection:** while a title is being typed, show existing posts with similar titles using `difflib`, to cut down on duplicate questions.
- **Knowledge-gap insight:** show managers which topics have the most unsolved posts, to help spot where training is needed.

**Also worth considering**

- **Post templates:** prefill the editor with headings for a Fix, How-to or Config post.
- **"Might be out of date" flag:** old technical posts show a warning and a *Still accurate* button.
- **Related posts on tasks:** show matching posts on a project task's detail screen.
- **Quick search:** Ctrl+K opens search from anywhere using `QShortcut`.

---

## Diagram source files

Editable versions are in `docs/diagrams/`: `posts_feed_generation.drawio`, `posts_feed_user_actions.drawio` and `posts_class_diagram.drawio`. Import them into Visual Paradigm Online with **Diagram > Open From Device**, then **File > Save as > VP Online**. They also open in [draw.io](https://app.diagrams.net).
