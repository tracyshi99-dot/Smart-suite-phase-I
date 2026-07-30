"""
i18n - Internationalization strings for Smart Suite UI.
Supports 5 languages: en, zh-CN, zh-TW, ko, vi

Usage:
    from i18n import t, set_language
    set_language("zh-TW")
    label = t("nav.overview")  # returns "總覽"
"""

_current_lang = "en"

# Translation dictionary: key → {lang_code: translation}
STRINGS = {
    # === Navigation ===
    "nav.overview": {
        "en": "Overview",
        "zh-CN": "总览",
        "zh-TW": "總覽",
        "ko": "개요",
        "vi": "Tổng quan",
    },
    "nav.research": {
        "en": "Research",
        "zh-CN": "智库",
        "zh-TW": "智庫",
        "ko": "리서치",
        "vi": "Nghiên cứu",
    },
    "nav.testing": {
        "en": "Testing",
        "zh-CN": "智测",
        "zh-TW": "智測",
        "ko": "테스팅",
        "vi": "Kiểm thử",
    },
    "nav.creation": {
        "en": "Creation",
        "zh-CN": "智造",
        "zh-TW": "智造",
        "ko": "콘텐츠 생성",
        "vi": "Sáng tạo",
    },
    "nav.optimization": {
        "en": "Optimization",
        "zh-CN": "智优",
        "zh-TW": "智優",
        "ko": "최적화",
        "vi": "Tối ưu hóa",
    },
    "nav.publishing": {
        "en": "Publishing",
        "zh-CN": "智布",
        "zh-TW": "智佈",
        "ko": "퍼블리싱",
        "vi": "Xuất bản",
    },
    "nav.distribution": {
        "en": "Distribution",
        "zh-CN": "智传",
        "zh-TW": "智傳",
        "ko": "배포",
        "vi": "Phân phối",
    },
    "nav.analytics": {
        "en": "Analytics",
        "zh-CN": "智析",
        "zh-TW": "智析",
        "ko": "분석",
        "vi": "Phân tích",
    },
    "nav.hub": {
        "en": "Hub",
        "zh-CN": "智中枢",
        "zh-TW": "智中樞",
        "ko": "허브",
        "vi": "Trung tâm",
    },

    # === Common UI Elements ===
    "common.login": {
        "en": "Login",
        "zh-CN": "登录",
        "zh-TW": "登入",
        "ko": "로그인",
        "vi": "Đăng nhập",
    },
    "common.logout": {
        "en": "Sign out",
        "zh-CN": "退出",
        "zh-TW": "登出",
        "ko": "로그아웃",
        "vi": "Đăng xuất",
    },
    "common.save": {
        "en": "Save",
        "zh-CN": "保存",
        "zh-TW": "儲存",
        "ko": "저장",
        "vi": "Lưu",
    },
    "common.cancel": {
        "en": "Cancel",
        "zh-CN": "取消",
        "zh-TW": "取消",
        "ko": "취소",
        "vi": "Hủy",
    },
    "common.confirm": {
        "en": "Confirm",
        "zh-CN": "确认",
        "zh-TW": "確認",
        "ko": "확인",
        "vi": "Xác nhận",
    },
    "common.delete": {
        "en": "Delete",
        "zh-CN": "删除",
        "zh-TW": "刪除",
        "ko": "삭제",
        "vi": "Xóa",
    },
    "common.edit": {
        "en": "Edit",
        "zh-CN": "编辑",
        "zh-TW": "編輯",
        "ko": "편집",
        "vi": "Chỉnh sửa",
    },
    "common.search": {
        "en": "Search",
        "zh-CN": "搜索",
        "zh-TW": "搜尋",
        "ko": "검색",
        "vi": "Tìm kiếm",
    },
    "common.loading": {
        "en": "Loading...",
        "zh-CN": "加载中...",
        "zh-TW": "載入中...",
        "ko": "로딩 중...",
        "vi": "Đang tải...",
    },
    "common.error": {
        "en": "Error",
        "zh-CN": "错误",
        "zh-TW": "錯誤",
        "ko": "오류",
        "vi": "Lỗi",
    },
    "common.success": {
        "en": "Success",
        "zh-CN": "成功",
        "zh-TW": "成功",
        "ko": "성공",
        "vi": "Thành công",
    },
    "common.warning": {
        "en": "Warning",
        "zh-CN": "警告",
        "zh-TW": "警告",
        "ko": "경고",
        "vi": "Cảnh báo",
    },
    "common.select": {
        "en": "Select",
        "zh-CN": "选择",
        "zh-TW": "選擇",
        "ko": "선택",
        "vi": "Chọn",
    },
    "common.all": {
        "en": "All",
        "zh-CN": "全部",
        "zh-TW": "全部",
        "ko": "전체",
        "vi": "Tất cả",
    },
    "common.none": {
        "en": "None",
        "zh-CN": "无",
        "zh-TW": "無",
        "ko": "없음",
        "vi": "Không có",
    },
    "common.download": {
        "en": "Download",
        "zh-CN": "下载",
        "zh-TW": "下載",
        "ko": "다운로드",
        "vi": "Tải xuống",
    },
    "common.upload": {
        "en": "Upload",
        "zh-CN": "上传",
        "zh-TW": "上傳",
        "ko": "업로드",
        "vi": "Tải lên",
    },
    "common.refresh": {
        "en": "Refresh",
        "zh-CN": "刷新",
        "zh-TW": "重新整理",
        "ko": "새로고침",
        "vi": "Làm mới",
    },
    "common.reset": {
        "en": "Reset",
        "zh-CN": "重置",
        "zh-TW": "重設",
        "ko": "초기화",
        "vi": "Đặt lại",
    },
    "common.close": {
        "en": "Close",
        "zh-CN": "关闭",
        "zh-TW": "關閉",
        "ko": "닫기",
        "vi": "Đóng",
    },
    "common.back": {
        "en": "Back",
        "zh-CN": "返回",
        "zh-TW": "返回",
        "ko": "뒤로",
        "vi": "Quay lại",
    },
    "common.next": {
        "en": "Next",
        "zh-CN": "下一步",
        "zh-TW": "下一步",
        "ko": "다음",
        "vi": "Tiếp theo",
    },
    "common.previous": {
        "en": "Previous",
        "zh-CN": "上一步",
        "zh-TW": "上一步",
        "ko": "이전",
        "vi": "Trước đó",
    },
    "common.run": {
        "en": "Run",
        "zh-CN": "运行",
        "zh-TW": "執行",
        "ko": "실행",
        "vi": "Chạy",
    },
    "common.stop": {
        "en": "Stop",
        "zh-CN": "停止",
        "zh-TW": "停止",
        "ko": "중지",
        "vi": "Dừng",
    },
    "common.results": {
        "en": "Results",
        "zh-CN": "结果",
        "zh-TW": "結果",
        "ko": "결과",
        "vi": "Kết quả",
    },
    "common.status": {
        "en": "Status",
        "zh-CN": "状态",
        "zh-TW": "狀態",
        "ko": "상태",
        "vi": "Trạng thái",
    },
    "common.history": {
        "en": "History",
        "zh-CN": "历史记录",
        "zh-TW": "歷史紀錄",
        "ko": "기록",
        "vi": "Lịch sử",
    },
    "common.items": {
        "en": "items",
        "zh-CN": "条",
        "zh-TW": "筆",
        "ko": "건",
        "vi": "mục",
    },

    # === Sidebar ===
    "sidebar.language": {
        "en": "Language",
        "zh-CN": "语言",
        "zh-TW": "語言",
        "ko": "언어",
        "vi": "Ngôn ngữ",
    },
    "sidebar.region": {
        "en": "Region",
        "zh-CN": "区域",
        "zh-TW": "區域",
        "ko": "지역",
        "vi": "Khu vực",
    },
    "sidebar.sub_region": {
        "en": "Sub-region",
        "zh-CN": "子区域",
        "zh-TW": "子區域",
        "ko": "하위 지역",
        "vi": "Phân vùng",
    },
    "sidebar.content_language": {
        "en": "Content Language",
        "zh-CN": "内容语言",
        "zh-TW": "內容語言",
        "ko": "콘텐츠 언어",
        "vi": "Ngôn ngữ nội dung",
    },
    "sidebar.login_name": {
        "en": "Your login name",
        "zh-CN": "您的登录名",
        "zh-TW": "您的登入名稱",
        "ko": "로그인 이름",
        "vi": "Tên đăng nhập",
    },
    "sidebar.access_denied": {
        "en": "Access denied",
        "zh-CN": "无权限，请联系管理员",
        "zh-TW": "無權限，請聯繫管理員",
        "ko": "접근이 거부되었습니다",
        "vi": "Truy cập bị từ chối",
    },
    "sidebar.demo_mode": {
        "en": "Demo",
        "zh-CN": "演示模式",
        "zh-TW": "展示模式",
        "ko": "데모",
        "vi": "Chế độ demo",
    },

    # === Zhiku (Research) ===
    "zhiku.title": {
        "en": "Query Library",
        "zh-CN": "智库 – 检索短语产出与验证",
        "zh-TW": "智庫 – 檢索短語產出與驗證",
        "ko": "쿼리 라이브러리",
        "vi": "Thư viện truy vấn",
    },
    "zhiku.subtitle": {
        "en": "Produce → Calibrate → Dedupe → Select → Verify Gap → Confirm",
        "zh-CN": "产出 → 校准 → 去重 → 选取 → 验证Gap → 确认进智造",
        "zh-TW": "產出 → 校準 → 去重 → 選取 → 驗證Gap → 確認進智造",
        "ko": "생성 → 보정 → 중복제거 → 선택 → 갭 검증 → 확인",
        "vi": "Tạo → Hiệu chỉnh → Loại trùng → Chọn → Xác minh Gap → Xác nhận",
    },
    "zhiku.seed_expansion": {
        "en": "Seed Expansion",
        "zh-CN": "词根裂变",
        "zh-TW": "詞根裂變",
        "ko": "시드 확장",
        "vi": "Mở rộng từ khóa gốc",
    },
    "zhiku.persona_expansion": {
        "en": "Persona Expansion",
        "zh-CN": "画像裂变",
        "zh-TW": "畫像裂變",
        "ko": "페르소나 확장",
        "vi": "Mở rộng chân dung",
    },
    "zhiku.upload_phrases": {
        "en": "Upload Phrases",
        "zh-CN": "上传检索短语",
        "zh-TW": "上傳檢索短語",
        "ko": "구문 업로드",
        "vi": "Tải lên cụm từ",
    },
    "zhiku.seed_word": {
        "en": "Seed word",
        "zh-CN": "词根",
        "zh-TW": "詞根",
        "ko": "시드 단어",
        "vi": "Từ khóa gốc",
    },
    "zhiku.expand": {
        "en": "Expand",
        "zh-CN": "开始裂变",
        "zh-TW": "開始裂變",
        "ko": "확장",
        "vi": "Mở rộng",
    },
    "zhiku.expanding": {
        "en": "Expanding...",
        "zh-CN": "裂变中...",
        "zh-TW": "裂變中...",
        "ko": "확장 중...",
        "vi": "Đang mở rộng...",
    },
    "zhiku.count": {
        "en": "Count",
        "zh-CN": "裂变数量",
        "zh-TW": "裂變數量",
        "ko": "생성 수",
        "vi": "Số lượng",
    },
    "zhiku.enter_seed": {
        "en": "Enter seed words, AI expands into search phrases",
        "zh-CN": "输入词根，AI 自动裂变出检索短语",
        "zh-TW": "輸入詞根，AI 自動裂變出檢索短語",
        "ko": "시드 단어를 입력하면 AI가 검색 구문을 생성합니다",
        "vi": "Nhập từ khóa gốc, AI tự động mở rộng thành cụm từ tìm kiếm",
    },

    # === Zhice (Testing) ===
    "zhice.title": {
        "en": "AI Search Journey Simulation",
        "zh-CN": "智测 – AI 搜索旅程模拟",
        "zh-TW": "智測 – AI 搜尋旅程模擬",
        "ko": "AI 검색 여정 시뮬레이션",
        "vi": "Mô phỏng hành trình tìm kiếm AI",
    },
    "zhice.platforms": {
        "en": "AI Platforms",
        "zh-CN": "AI 平台",
        "zh-TW": "AI 平台",
        "ko": "AI 플랫폼",
        "vi": "Nền tảng AI",
    },
    "zhice.run_simulation": {
        "en": "Run Simulation",
        "zh-CN": "开始模拟",
        "zh-TW": "開始模擬",
        "ko": "시뮬레이션 실행",
        "vi": "Chạy mô phỏng",
    },
    "zhice.coverage": {
        "en": "Coverage",
        "zh-CN": "覆盖率",
        "zh-TW": "覆蓋率",
        "ko": "커버리지",
        "vi": "Độ phủ",
    },
    "zhice.brand_mentioned": {
        "en": "Brand Mentioned",
        "zh-CN": "品牌提及",
        "zh-TW": "品牌提及",
        "ko": "브랜드 언급",
        "vi": "Đề cập thương hiệu",
    },
    "zhice.official_link": {
        "en": "Official Link",
        "zh-CN": "官方链接",
        "zh-TW": "官方連結",
        "ko": "공식 링크",
        "vi": "Liên kết chính thức",
    },

    # === Zhizao (Creation) ===
    "zhizao.title": {
        "en": "Content Creation",
        "zh-CN": "智造 – 内容生成",
        "zh-TW": "智造 – 內容生成",
        "ko": "콘텐츠 생성",
        "vi": "Tạo nội dung",
    },
    "zhizao.generate": {
        "en": "Generate Content",
        "zh-CN": "生成内容",
        "zh-TW": "生成內容",
        "ko": "콘텐츠 생성",
        "vi": "Tạo nội dung",
    },
    "zhizao.article": {
        "en": "Article",
        "zh-CN": "文章",
        "zh-TW": "文章",
        "ko": "기사",
        "vi": "Bài viết",
    },

    # === Zhiyou (Optimization) ===
    "zhiyou.title": {
        "en": "Content Optimization",
        "zh-CN": "智优 – 内容优化",
        "zh-TW": "智優 – 內容優化",
        "ko": "콘텐츠 최적화",
        "vi": "Tối ưu hóa nội dung",
    },
    "zhiyou.score": {
        "en": "Score",
        "zh-CN": "评分",
        "zh-TW": "評分",
        "ko": "점수",
        "vi": "Điểm",
    },
    "zhiyou.rewrite": {
        "en": "Rewrite",
        "zh-CN": "重写",
        "zh-TW": "重寫",
        "ko": "재작성",
        "vi": "Viết lại",
    },
    "zhiyou.compliance": {
        "en": "Compliance Check",
        "zh-CN": "合规检查",
        "zh-TW": "合規檢查",
        "ko": "규정 준수 확인",
        "vi": "Kiểm tra tuân thủ",
    },

    # === Zhibu (Publishing) ===
    "zhibu.title": {
        "en": "Content Publishing",
        "zh-CN": "智布 – 内容发布",
        "zh-TW": "智佈 – 內容發佈",
        "ko": "콘텐츠 퍼블리싱",
        "vi": "Xuất bản nội dung",
    },
    "zhibu.export_json": {
        "en": "Export JSON",
        "zh-CN": "导出 JSON",
        "zh-TW": "匯出 JSON",
        "ko": "JSON 내보내기",
        "vi": "Xuất JSON",
    },

    # === Zhixi (Analytics) ===
    "zhixi.title": {
        "en": "Analytics Dashboard",
        "zh-CN": "智析 – 数据分析",
        "zh-TW": "智析 – 數據分析",
        "ko": "분석 대시보드",
        "vi": "Bảng phân tích",
    },
    "zhixi.weekly_trend": {
        "en": "Weekly Trend",
        "zh-CN": "周趋势",
        "zh-TW": "週趨勢",
        "ko": "주간 추세",
        "vi": "Xu hướng tuần",
    },
    "zhixi.ytd_summary": {
        "en": "YTD Summary",
        "zh-CN": "年度累计",
        "zh-TW": "年度累計",
        "ko": "연간 누적",
        "vi": "Lũy kế năm",
    },

    # === Admin ===
    "admin.title": {
        "en": "Admin Panel",
        "zh-CN": "管理面板",
        "zh-TW": "管理面板",
        "ko": "관리 패널",
        "vi": "Bảng quản trị",
    },
    "admin.approve": {
        "en": "Approve",
        "zh-CN": "批准",
        "zh-TW": "核准",
        "ko": "승인",
        "vi": "Phê duyệt",
    },
    "admin.reject": {
        "en": "Reject",
        "zh-CN": "拒绝",
        "zh-TW": "拒絕",
        "ko": "거부",
        "vi": "Từ chối",
    },
    "admin.pending": {
        "en": "Pending",
        "zh-CN": "待审批",
        "zh-TW": "待審批",
        "ko": "대기 중",
        "vi": "Đang chờ",
    },
    "admin.user_list": {
        "en": "User List",
        "zh-CN": "用户列表",
        "zh-TW": "使用者列表",
        "ko": "사용자 목록",
        "vi": "Danh sách người dùng",
    },
    "admin.region_filter": {
        "en": "Filter by Region",
        "zh-CN": "按区域筛选",
        "zh-TW": "依區域篩選",
        "ko": "지역별 필터",
        "vi": "Lọc theo khu vực",
    },

    # === Batch / Pipeline ===
    "batch.select": {
        "en": "Select Batch",
        "zh-CN": "选择批次",
        "zh-TW": "選擇批次",
        "ko": "배치 선택",
        "vi": "Chọn lô",
    },
    "pipeline.full_run": {
        "en": "Full Pipeline Run",
        "zh-CN": "全流程运行",
        "zh-TW": "全流程執行",
        "ko": "전체 파이프라인 실행",
        "vi": "Chạy toàn bộ quy trình",
    },

    # === Login Page ===
    "login.please_login": {
        "en": "Please log in to access Smart Suite tools",
        "zh-CN": "请先登录",
        "zh-TW": "請先登入",
        "ko": "Smart Suite 도구에 접근하려면 로그인하세요",
        "vi": "Vui lòng đăng nhập để sử dụng Smart Suite",
    },
    "login.select_name": {
        "en": "Select your name below or enter login in the sidebar.",
        "zh-CN": "从下方选择您的名称，或在左侧栏输入 Login。",
        "zh-TW": "從下方選擇您的名稱，或在側邊欄輸入登入名。",
        "ko": "아래에서 이름을 선택하거나 사이드바에서 로그인을 입력하세요.",
        "vi": "Chọn tên bên dưới hoặc nhập đăng nhập ở thanh bên.",
    },
}


def set_language(lang_code: str):
    """Set the active UI language."""
    global _current_lang
    if lang_code in ("en", "zh-CN", "zh-TW", "ko", "vi"):
        _current_lang = lang_code


def get_language() -> str:
    """Get current active UI language code."""
    return _current_lang


def t(key: str, lang: str = None) -> str:
    """Translate a key to the current (or specified) language.
    Falls back to English if key or language not found.
    """
    lang = lang or _current_lang
    entry = STRINGS.get(key)
    if not entry:
        return key  # Key not found, return as-is
    # Try exact match
    if lang in entry:
        return entry[lang]
    # Fallback: zh-TW → zh-CN → en
    if lang == "zh-TW" and "zh-CN" in entry:
        return entry["zh-CN"]
    if lang.startswith("zh") and "zh-CN" in entry:
        return entry["zh-CN"]
    return entry.get("en", key)
