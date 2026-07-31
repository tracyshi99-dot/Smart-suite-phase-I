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
    text = _clean_markdown(text)
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


def _heading_widget(text: str, level="1", font_size=None):
    """Create a Heading widget with clear size hierarchy.
    LEGO tokens: xlarge > large > medium > small > xsmall
    H1 = xlarge (page title), H2 = large (section), H3 = medium (sub-section)
    """
    text = _clean_markdown(text)
    if font_size is None:
        font_size = {"1": "xlarge", "2": "large", "3": "medium"}.get(str(level), "medium")
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


def _clean_markdown(text: str) -> str:
    """Remove markdown formatting artifacts (bold, italic, headers markers)."""
    # Remove bold **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    # Remove italic *text* or _text_ (but not underscores in words)
    text = re.sub(r'(?<!\w)\*(.+?)\*(?!\w)', r'\1', text)
    # Remove heading markers at start of line
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bullet markers at start (- or *)
    text = re.sub(r'^[\-\*]\s+', '', text, flags=re.MULTILINE)
    return text.strip()


def _table_cell_container(text: str, width: int, is_header: bool = False):
    """Create a table cell as a Container with border."""
    bg = "siren" if is_header else "white"
    txt_color = "white" if is_header else "squid-ink"
    txt_weight = "bold" if is_header else "normal"
    alignment = "center" if is_header else "start"
    text = _clean_markdown(text.strip())

    cell_widget = {
        "content": _draft_block(text),
        "alignmentDesktop": alignment, "alignmentTablet": "desktop",
        "alignmentMobileportrait": "tablet", "alignmentMobilelandscape": "tablet",
        "disableTranslatable": False,
        "fontSizeDesktop": "small", "fontSizeTablet": "desktop",
        "fontSizeMobileportrait": "tablet", "fontSizeMobilelandscape": "tablet",
        "fontFamily": "ember", "color": txt_color, "fontWeight": txt_weight,
        "useTooltip": False, "tooltipStyle": "light", "tooltipContent": "",
        "widgetClassName": "Text",
        "reusable": None, "reusablePlaceholder": None,
        "id": _gen_id()
    }

    return _base_container(
        widgets=[cell_widget],
        widthDesktop=width,
        widthTablet=width,
        widthMobileportrait=12,
        widthMobilelandscape=12,
        backgroundColor=bg,
        borderColor="mercury",
        borderWidthTopDesktop="thin",
        borderWidthTopTablet="desktop",
        borderWidthTopMobileportrait="tablet",
        borderWidthTopMobilelandscape="tablet",
        borderWidthLeftDesktop="thin",
        borderWidthLeftTablet="desktop",
        borderWidthLeftMobileportrait="tablet",
        borderWidthLeftMobilelandscape="tablet",
        borderWidthRightDesktop="thin",
        borderWidthRightTablet="desktop",
        borderWidthRightMobileportrait="tablet",
        borderWidthRightMobilelandscape="tablet",
        borderWidthBottomDesktop="thin",
        borderWidthBottomTablet="desktop",
        borderWidthBottomMobileportrait="tablet",
        borderWidthBottomMobilelandscape="tablet",
        paddingTopDesktop="xmini",
        paddingTopTablet="desktop",
        paddingLeftDesktop="mini",
        paddingLeftTablet="desktop",
        paddingRightDesktop="mini",
        paddingRightTablet="desktop",
        paddingBottomDesktop="xmini",
        paddingBottomTablet="desktop",
        noWrap=True,
    )


def _table_row_container(cells: list, col_widths: list, is_header: bool = False):
    """Create a table row as a Container with columns (inline flex row)."""
    cell_containers = []
    for i, cell_text in enumerate(cells):
        w = col_widths[i] if i < len(col_widths) else 12 // len(cells)
        cell_containers.append(_table_cell_container(cell_text, w, is_header))

    return _base_container(
        widgets=cell_containers,
        widthDesktop=12,
        widthTablet=12,
        widthMobileportrait=12,
        widthMobilelandscape=12,
        noWrap=True,
        isMobileRow=True,
        horizontalAlignmentDesktop="default",
        verticalItemsAlignmentDesktop="stretch",
        paddingTopDesktop="zero",
        paddingBottomDesktop="zero",
        paddingLeftDesktop="zero",
        paddingRightDesktop="zero",
    )


def _markdown_table_to_containers(table_lines: list) -> list:
    """Convert markdown table lines into LEGO Container rows."""
    if len(table_lines) < 2:
        return []

    # Parse header
    header_cells = [c.strip() for c in table_lines[0].split("|") if c.strip()]
    num_cols = len(header_cells)
    if num_cols == 0:
        return []

    # Calculate column widths based on content length
    # Collect all cells to measure max width per column
    all_rows_cells = [header_cells]
    for line in table_lines[1:]:
        if re.match(r'^\s*\|[\s\-:]+\|', line):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if cells:
            while len(cells) < num_cols:
                cells.append("")
            all_rows_cells.append(cells[:num_cols])

    # Measure max content length per column
    col_max_len = [0] * num_cols
    for row in all_rows_cells:
        for i, cell in enumerate(row):
            col_max_len[i] = max(col_max_len[i], len(cell))

    # Distribute 12 grid units proportionally to content width
    total_len = sum(col_max_len) or 1
    col_widths = [max(2, round(12 * (l / total_len))) for l in col_max_len]
    # Adjust to sum to 12
    diff = sum(col_widths) - 12
    if diff > 0:
        # Reduce widest columns
        for _ in range(abs(diff)):
            widest = col_widths.index(max(col_widths))
            col_widths[widest] -= 1
    elif diff < 0:
        # Increase narrowest
        for _ in range(abs(diff)):
            narrowest = col_widths.index(min(col_widths))
            col_widths[narrowest] += 1

    rows = []
    # Header row
    rows.append(_table_row_container(header_cells, col_widths, is_header=True))

    # Data rows (skip separator line like |---|---|)
    for line in table_lines[1:]:
        if re.match(r'^\s*\|[\s\-:]+\|', line):
            continue  # Skip separator
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if cells:
            while len(cells) < num_cols:
                cells.append("")
            rows.append(_table_row_container(cells[:num_cols], col_widths, is_header=False))

    # Wrap all rows in a table container (no extra padding to avoid overflow)
    return [_base_container(
        widgets=rows,
        widthDesktop=12,
        widthTablet=12,
        widthMobileportrait=12,
        borderRadiusDesktop="9px",
        hasBoxShadow=False,
        backgroundColor="transparent",
        paddingTopDesktop="mini",
        paddingBottomDesktop="mini",
        paddingLeftDesktop="zero",
        paddingRightDesktop="zero",
    )]


def _parse_markdown_sections(content: str) -> dict:
    """Parse markdown content into sections, extracting tables separately."""
    sections = {"overview": "", "body_sections": [], "faq": ""}
    lines = content.split("\n")
    current_section = "overview"
    current_text = []
    current_heading = ""
    in_table = False
    table_lines = []

    for line in lines:
        # Detect table lines
        is_table_line = "|" in line and line.strip().startswith("|") and line.strip().endswith("|") and line.count("|") >= 3

        if is_table_line:
            # Starting or continuing a table
            if not in_table:
                # Save any text before table
                if current_text:
                    text = "\n".join(current_text).strip()
                    if current_section == "overview":
                        sections["overview"] = text
                    elif current_section == "faq":
                        sections["faq"] += "\n" + text if sections["faq"] else text
                    else:
                        sections["body_sections"].append({"heading": current_heading, "content": text, "type": "text"})
                    current_text = []
                    current_heading = ""
                in_table = True
            table_lines.append(line)
        else:
            if in_table:
                # Table ended, save it
                sections["body_sections"].append({"heading": "", "content": table_lines[:], "type": "table"})
                table_lines = []
                in_table = False

            # H2 heading starts a new section
            if line.startswith("## "):
                if current_text:
                    text = "\n".join(current_text).strip()
                    if current_section == "overview":
                        sections["overview"] = text
                    elif current_section == "faq":
                        sections["faq"] += "\n" + text if sections["faq"] else text
                    else:
                        sections["body_sections"].append({"heading": current_heading, "content": text, "type": "text"})
                current_heading = line.lstrip("# ").strip()
                current_text = []
                current_section = "body"
                if any(kw in current_heading.lower() for kw in ["faq", "常见问题", "common question"]):
                    current_section = "faq"
            else:
                current_text.append(line)

    # Save remaining
    if in_table and table_lines:
        sections["body_sections"].append({"heading": "", "content": table_lines[:], "type": "table"})
    elif current_text:
        text = "\n".join(current_text).strip()
        if current_section == "overview":
            sections["overview"] = text
        elif current_section == "faq":
            sections["faq"] += "\n" + text if sections["faq"] else text
        else:
            sections["body_sections"].append({"heading": current_heading, "content": text, "type": "text"})

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

    # 2. Title section (H1 — large font)
    title_container = _base_container(
        widgets=[_heading_widget(title, level="1")],
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

    # 4. Body sections (each H2 section becomes a container, tables get special rendering)
    for sec in sections["body_sections"]:
        sec_type = sec.get("type", "text")

        # Sub-title (for text sections) — H2 heading widget with medium font
        if sec.get("heading") and sec_type == "text":
            st_container = _base_container(
                widgets=[_heading_widget(sec["heading"], level="2")],
                paddingTopDesktop="base"
            )
            containers.append(st_container)

        if sec_type == "table":
            # Render markdown table as LEGO grid
            table_containers = _markdown_table_to_containers(sec["content"])
            containers.extend(table_containers)
        elif sec.get("content"):
            # Regular text content — split by H3 headings for proper hierarchy
            content_lines = sec["content"].split("\n")
            current_block = []
            for line in content_lines:
                if line.startswith("### "):
                    # Flush previous block
                    if current_block:
                        block_text = "\n".join(current_block).strip()
                        if block_text:
                            containers.append(_base_container(
                                widgets=[_text_widget(block_text, font_size="small", color="storm")]
                            ))
                        current_block = []
                    # H3 heading
                    h3_text = line.lstrip("# ").strip()
                    containers.append(_base_container(
                        widgets=[_heading_widget(h3_text, level="3")],
                        paddingTopDesktop="mini"
                    ))
                else:
                    current_block.append(line)
            # Flush remaining
            if current_block:
                block_text = "\n".join(current_block).strip()
                if block_text:
                    containers.append(_base_container(
                        widgets=[_text_widget(block_text, font_size="small", color="storm")]
                    ))

    # 5. FAQ section (if exists)
    if sections["faq"]:
        faq_heading = _base_container(
            widgets=[_heading_widget("常见问题 / FAQ", level="2")],
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

    # Generate meta description from overview (first 150 chars of content, stripped of markdown)
    clean_content = _clean_markdown(content)
    # Take first paragraph or first 160 chars for meta description
    first_para = clean_content.split("\n\n")[0] if "\n\n" in clean_content else clean_content[:200]
    meta_desc = first_para[:160].strip()
    if len(first_para) > 160:
        meta_desc = meta_desc[:157] + "..."

    # Meta title: article title + brand suffix
    meta_title = f"{_clean_markdown(title)}_Amazon亚马逊"

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
    # Add meta fields
    page["metaTitle"] = meta_title
    page["metaDescription"] = meta_desc
    return page
