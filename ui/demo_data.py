"""
Demo data for Streamlit Cloud deployment (when local output/ is not available).
"""
import pandas as pd


def get_demo_keywords():
    return pd.DataFrame({
        "keyword_id": ["KW_001", "KW_002", "KW_010", "KW_011", "KW_012", "KW_013"],
        "Keyword": ["亚马逊", "amazon", "amazon seller", "亚马逊跨境电商平台官网", "亚马逊北美站", "亚马逊美国站"],
        "market": ["CN", "CN", "CN", "CN", "CN", "CN"],
        "language": ["zh", "zh", "zh", "zh", "zh", "zh"],
        "keyword_type": ["branded", "branded", "branded", "branded", "branded", "branded"],
        "search_volumn": ["323,753", "102,516", "8,200", "5,400", "4,100", "3,800"],
        "conversion_value": ["high", "high", "high", "high", "high", "high"],
        "priority": [5, 5, 5, 5, 5, 4],
    })


def get_demo_zhiku():
    return pd.DataFrame({
        "keyword": ["amazon seller", "amazon seller", "亚马逊跨境电商平台官网", "亚马逊北美站"],
        "ai_query": [
            "如何成为Amazon Seller？中国卖家注册亚马逊卖家账户的完整指南",
            "Amazon Seller Central后台有哪些核心功能？",
            "亚马逊跨境电商平台提供哪些服务？中国卖家如何利用平台资源实现出海？",
            "亚马逊北美站包含哪些国家？各站点有什么特点和机会？",
        ],
        "intent_type": ["informational", "informational", "informational", "informational"],
        "priority_score": [5, 4, 5, 5],
        "is_selected": ["TRUE", "TRUE", "TRUE", "TRUE"],
    })


def get_demo_scorecard():
    return pd.DataFrame({
        "content_id": ["C_011", "C_012", "C_013", "C_014"],
        "ai_query": [
            "如何成为Amazon Seller？中国卖家注册亚马逊卖家账户的完整指南",
            "亚马逊北美站包含哪些国家？各站点有什么特点和机会？",
            "亚马逊美国站的市场规模和竞争格局是怎样的？",
            "如何打造一个高转化的亚马逊品牌店铺？",
        ],
        "intent_match_score": [5, 5, 5, 5],
        "ai_readability_score": [5, 5, 5, 5],
        "authority_score": [4, 5, 4, 5],
        "actionability_score": [5, 5, 4, 5],
        "differentiation_score": [4, 4, 4, 5],
        "overall_score": [4.70, 4.90, 4.50, 5.00],
        "is_approved": ["TRUE", "TRUE", "TRUE", "TRUE"],
    })


def get_demo_batch_summary():
    return pd.DataFrame({
        "batch_id": ["batch_003"],
        "total_keywords": [6],
        "total_queries": [10],
        "selected_queries": [8],
        "generated_content": [4],
        "approved_content": [4],
        "avg_overall_score": [4.78],
        "completion_rate": ["100%"],
    })
