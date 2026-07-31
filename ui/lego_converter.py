"""
LEGO Sell Design JSON Converter
Converts Markdown articles into LEGO CMS Sell Design format.
Each article becomes a page with sections: label, title, overview, content, data, remark.
"""
import json
import re
import uuid
from datetime import datetime


def _gen_id():
    return str(uuid.uuid4())


def _gen_uuid():
    return str(uuid.uuid4())


def _draft_block(text: str, block_type="unstyled", inline_styles=None, entity_ranges=None):
    """Create a Draft.js content JSON string."""
    block = {
        "key": "1e07k",
        "text": text,
        "type": block_type,
        "depth": 0,
        "inlineStyleRanges": inline_styles or [],
        "entityRanges": entity_ranges or [],
        "data": {}
    }
    entity_map = {}
    # Auto-detect links in text
    link_pattern = re.compile(r'(https?://\S+)')
    entities = []
    for match in link_pattern.finditer(text):
        key = len(entities)
        entities.append({
            "offset": match.start(),
            "length": len(match.group()),
            "key": key
        })
        entity_map[str(key)] = {
            "type": "LINK",
            "mutability": "MUTABLE",
            "data": {"url": match.group()}
        }
    if entities:
        block["entityRanges"] = entities
    return json.dumps({"blocks": [block], "entityMap": entity_map}, ensure_ascii=False)


def _base_container(widget_id=None, widgets=None, **overrides):
    """Create a base LEGO Container with default Sell Design settings."""
    container = {
        "borderRadiusDesktop": "none",
        "borderRadiusTablet": "desktop",
        "borderRadiusMobileportrait": "tablet",
        "borderRadiusMobilelandscape": "tablet",
        "widthDesktop": 12,
        "widthTablet": 12,
        "widthMobileportrait": 12,
        "widthMobilelandscape": 12,
        "imageOrVideoBg": "image",
        "backgroundURL": "",
        "videoBackgroundURL": "",
        "secondaryVideoBackgroundURL": "",
        "posterURL": "",
        "videoAttrs": ["autoPlay", "muted", "loop", "playsInline"],
        "videoCaptions": [],
        "backgroundPosition": "center center",
        "backgroundSize": "cover",
        "backgroundRepeat": "no-repeat",
        "hyphens": "manual",
        "overflowWrap": "normal",
        "wordBreak": "normal",
        "elementId": "",
        "cssClass": "",
        "data": [],
        "language": "default",
        "deviceColumnsTablet": False,
        "deviceColumnsMobileportrait": False,
        "deviceColumnsMobilelandscape": False,
        "horizontalAlignmentDesktop": "default",
        "horizontalAlignmentTablet": "desktop",
        "horizontalAlignmentMobileportrait": "tablet",
        "horizontalAlignmentMobilelandscape": "tablet",
        "verticalItemsAlignmentDesktop": "stretch",
        "verticalItemsAlignmentTablet": "desktop",
        "verticalItemsAlignmentMobileportrait": "tablet",
        "verticalItemsAlignmentMobilelandscape": "tablet",
        "verticalContentAlignmentDesktop": "flex-start",
        "verticalContentAlignmentTablet": "desktop",
        "verticalContentAlignmentMobileportrait": "tablet",
        "verticalContentAlignmentMobilelandscape": "tablet",
        "isFullHeight": False,
        "hasMaxWidth": False,
        "deviceAvailability": ["desktop", "tablet", "mobilePortrait", "mobileLandscape"],
        "isSticky": False,
        "stickyPosition": "top",
        "animateOnScrollType": "none",
        "animateOnScrollDelay": "100",
        "animateOnScrollDuration": "600",
        "preventImageOptimization": False,
        "inputDependency": False,
        "inputDependencies": [],
        "queryDependency": False,
        "queryDependencies": [],
        "borderWidthTopDesktop": "zero", "borderWidthTopTablet": "desktop", "borderWidthTopMobileportrait": "tablet", "borderWidthTopMobilelandscape": "tablet",
        "borderWidthLeftDesktop": "zero", "borderWidthLeftTablet": "desktop", "borderWidthLeftMobileportrait": "tablet", "borderWidthLeftMobilelandscape": "tablet",
        "borderWidthRightDesktop": "zero", "borderWidthRightTablet": "desktop", "borderWidthRightMobileportrait": "tablet", "borderWidthRightMobilelandscape": "tablet",
        "borderWidthBottomDesktop": "zero", "borderWidthBottomTablet": "desktop", "borderWidthBottomMobileportrait": "tablet", "borderWidthBottomMobilelandscape": "tablet",
        "paddingTopDesktop": "mini", "paddingTopTablet": "zero", "paddingTopMobileportrait": "tablet", "paddingTopMobilelandscape": "tablet",
        "paddingLeftDesktop": "zero", "paddingLeftTablet": "zero", "paddingLeftMobileportrait": "tablet", "paddingLeftMobilelandscape": "tablet",
        "paddingRightDesktop": "zero", "paddingRightTablet": "desktop", "paddingRightMobileportrait": "tablet", "paddingRightMobilelandscape": "tablet",
        "paddingBottomDesktop": "zero", "paddingBottomTablet": "desktop", "paddingBottomMobileportrait": "tablet", "paddingBottomMobilelandscape": "tablet",
        "hasWave": False, "waveStyle": "style-1", "waveColor": "white", "flipWave": False, "wavePlacement": "bottom",
        "hasBoxShadow": False, "boxShadowType": "light",
        "isFluid": False, "noWrap": False, "isMobileRow": False,
        "backgroundColor": "transparent",
        "borderColor": "squid-ink",
        "gradientAngle": "0deg",
        "isSearchAnchor": False, "searchAnchorText": "",
        "hoverAnimation": "none", "hoverSpeed": "normal",
        "sellDesignSnippetClass": "",
        "tabId": "", "showTabOnLoad": False,
        "widgetClassName": "Container",
        "reusable": None, "reusablePlaceholder": None,
        "id": widget_id or _gen_id(),
        "widgets": widgets or [],
        "design": "Sell",
        "uuid": _gen_uuid(),
        "legoVersion": "2"
    }
    container.update(overrides)
    return container


def _text_widget(text: str, font_size="small", color="storm", font_weight="normal"):
    """Create a Text widget."""
    return {
        "content": _draft_block(text),
        "alignmentDesktop": "start", "alignmentTablet": "desktop",
        "alignmentMobileportrait": "tablet", "alignmentMobilelandscape": "tablet",
        "disableTranslatable": False,
        "fontSizeDesktop": font_size, "fontSizeTablet": "desktop",
        "fontSizeMobileportrait": "tablet", "fontSizeMobilelandscape": "tablet",
        "fontFamily": "ember", "color": color, "fontWeight": font_weight,
        "useTooltip": False, "tooltipStyle": "light", "tooltipContent": "",
        "widgetClassName": "Text",
        "reusable": None, "reusablePlaceholder": None,
        "id": _gen_id()
    }


def _heading_widget(text: str, level="1", font_size="medium"):
    """Create a Heading widget."""
    return {
        "content": _draft_block(text),
        "headingLevel": level,
        "alignmentDesktop": "start", "alignmentTablet": "desktop",
        "alignmentMobileportrait": "tablet", "alignmentMobilelandscape": "tablet",
        "disableTranslatable": False,
        "fontSizeDesktop": font_size, "fontSizeTablet": "desktop",
        "fontSizeMobileportrait": "tablet", "fontSizeMobilelandscape": "tablet",
        "color": "squid-ink", "fontFamily": "ember", "fontWeight": "bold",
        "useTooltip": False, "tooltipStyle": "light", "tooltipContent": "",
        "widgetClassName": "Heading",
        "reusable": None, "reusablePlaceholder": None,
        "id": _gen_id()
    }


def _parse_markdown_sections(content: str) -> dict:
    """Parse markdown content into sections."""
    sections = {"overview": "", "body_sections": [], "tables": [], "faq": ""}
    lines = content.split("\n")
    current_section = "overview"
    current_text = []
    current_heading = ""

    for line in lines:
        # H2 heading starts a new section
        if line.startswith("## "):
            # Save previous section
            if current_text:
                text = "\n".join(current_text).strip()
                if current_section == "overview":
                    sections["overview"] = text
                else:
                    sections["body_sections"].append({"heading": current_heading, "content": text})
            current_heading = line.lstrip("# ").strip()
            current_text = []
            current_section = "body"
            # Check if it's FAQ
            if any(kw in current_heading.lower() for kw in ["faq", "常见问题", "common question"]):
                current_section = "faq"
        elif "|---" in line or ("|" in line and line.count("|") >= 3):
            # Table line - collect for table sections
            if line not in [l for t in sections["tables"] for l in t]:
                # Find the full table
                pass
            current_text.append(line)
        else:
            current_text.append(line)

    # Save last section
    if current_text:
        text = "\n".join(current_text).strip()
        if current_section == "overview":
            sections["overview"] = text
        elif current_section == "faq":
            sections["faq"] = text
        else:
            sections["body_sections"].append({"heading": current_heading, "content": text})

    return sections


def markdown_to_lego(title: str, content: str, source_query: str = "",
                     label: str = "跨境知识荟", batch_id: str = "") -> list:
    """Convert a markdown article into LEGO Sell Design JSON sections.

    Returns a list of Container widgets representing the full page.
    """
    sections = _parse_markdown_sections(content)
    containers = []

    # 1. Label section
    label_container = _base_container(
        widgets=[_text_widget(label, font_size="xsmall", color="squid-ink")],
        paddingBottomDesktop="xsmall"
    )
    containers.append(label_container)

    # 2. Title section (H1)
    title_container = _base_container(
        widgets=[_heading_widget(title, level="1", font_size="medium")],
        paddingTopDesktop="zero", paddingBottomDesktop="mini"
    )
    containers.append(title_container)

    # 3. Overview section
    if sections["overview"]:
        overview_text = sections["overview"][:500]
        if not overview_text:
            overview_text = content[:200].replace("\n", " ").strip()
        overview_container = _base_container(
            widgets=[_text_widget(overview_text, font_size="small", color="stone")]
        )
        containers.append(overview_container)

    # 4. Body sections (each H2 section becomes a container)
    for sec in sections["body_sections"]:
        # Sub-title
        if sec["heading"]:
            st_container = _base_container(
                widgets=[_text_widget(sec["heading"], font_size="large", color="squid-ink", font_weight="bold")],
                paddingTopDesktop="base"
            )
            containers.append(st_container)

        # Content
        if sec["content"]:
            content_container = _base_container(
                widgets=[_text_widget(sec["content"], font_size="small", color="storm")]
            )
            containers.append(content_container)

    # 5. FAQ section (if exists)
    if sections["faq"]:
        faq_heading = _base_container(
            widgets=[_text_widget("常见问题 / FAQ", font_size="large", color="squid-ink", font_weight="bold")],
            paddingTopDesktop="base"
        )
        containers.append(faq_heading)
        faq_content = _base_container(
            widgets=[_text_widget(sections["faq"], font_size="small", color="storm")]
        )
        containers.append(faq_content)

    # 6. Data source section
    data_text = "数据来源：\n亚马逊全球开店官方指南（gs.amazon.cn）、亚马逊卖家中心官方政策文档"
    data_container = _base_container(
        widgets=[_text_widget(data_text, font_size="xsmall", color="storm")]
    )
    containers.append(data_container)

    # 7. Remark section
    remark_text = f"备注：以上信息更新时间为{datetime.now().strftime('%Y年%m月')}，关注全球开店官网及时了解最新变化。"
    remark_container = _base_container(
        widgets=[_text_widget(remark_text, font_size="small", color="storm")],
        paddingTopDesktop="base"
    )
    containers.append(remark_container)

    return containers


def convert_article_to_lego_page(title: str, content: str, source_query: str = "",
                                  label: str = "跨境知识荟", batch_id: str = "") -> dict:
    """Convert a single article into a complete LEGO page JSON.

    Returns a single top-level Container widget (Sell Design format)
    that can be directly imported into LEGO CMS.
    """
    containers = markdown_to_lego(title, content, source_query, label, batch_id)

    # Wrap all section containers into a single top-level Container
    page = _base_container(
        widgets=containers,
        hasMaxWidth=True,
        paddingTopDesktop="minibase",
        paddingTopTablet="base",
        paddingLeftDesktop="xxlarge",
        paddingLeftTablet="xsmall",
        paddingRightDesktop="xxlarge",
        paddingRightTablet="xsmall",
        paddingBottomDesktop="minibase",
        gradientAngle="90deg",
    )
    # Add required top-level fields
    page["design"] = "Sell"
    page["uuid"] = _gen_uuid()
    page["legoVersion"] = "2"
    return page
