# guides_catalog.py - Centralized guide definitions
# Import this wherever you need guide metadata (analytics, templates, routes)

GUIDES_CATALOG = {
    "what-is-a-prop-firm": {
        "title": "What is a Prop Firm?",
        "href": "/guides/what-is-a-prop-firm",
        "group": "Beginner Basics",
    },
    "what-is-futures-trading": {
        "title": "What is Futures Trading?",
        "href": "/guides/what-is-futures-trading",
        "group": "Beginner Basics",
    },
    "what-is-a-sim-account": {
        "title": "What is a Sim Account?",
        "href": "/guides/what-is-a-sim-account",
        "group": "Beginner Basics",
    },
    "what-is-an-evaluation": {
        "title": "What is a Prop Firm Evaluation?",
        "href": "/guides/what-is-an-evaluation",
        "group": "Beginner Basics",
    },
    "best-way-to-start-trading-futures": {
        "title": "Best Way to Start Trading Futures",
        "href": "/guides/best-way-to-start-trading-futures",
        "group": "Choosing an Account",
    },
    "best-prop-firm-to-start": {
        "title": "Best Prop Firm to Start With",
        "href": "/guides/best-prop-firm-to-start",
        "group": "Choosing an Account",
    },
    "best-account-size-to-start": {
        "title": "What Account Size Should I Start With?",
        "href": "/guides/best-account-size-to-start",
        "group": "Choosing an Account",
    },
    "should-i-skip-evaluation": {
        "title": "Should I Skip the Evaluation?",
        "href": "/guides/should-i-skip-evaluation",
        "group": "Choosing an Account",
    },
    "what-is-straight-to-sim-funded": {
        "title": "What is a Straight-to-Sim-Funded Account?",
        "href": "/guides/what-is-straight-to-sim-funded",
        "group": "Choosing an Account",
    },
    "personal-vs-prop-account": {
        "title": "Personal Account vs Prop Account",
        "href": "/guides/personal-vs-prop-account",
        "group": "Choosing an Account",
    },
    "futures-trading-products": {
        "title": "Futures Trading Products",
        "href": "/guides/futures-trading-products",
        "group": "Beginner Basics",
    },
}

# Helper functions for common operations
def get_guide_by_id(guide_id: str) -> dict | None:
    """Get guide metadata by ID"""
    return GUIDES_CATALOG.get(guide_id)

def get_guides_by_group(group: str) -> list[dict]:
    """Get all guides in a specific group"""
    return [
        {"id": gid, **guide} 
        for gid, guide in GUIDES_CATALOG.items() 
        if guide["group"] == group
    ]

def get_all_guides() -> list[dict]:
    """Get all guides with IDs included"""
    return [{"id": gid, **guide} for gid, guide in GUIDES_CATALOG.items()]