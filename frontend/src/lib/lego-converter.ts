/**
 * LEGO Sell Design JSON Converter
 * Converts article content into Amazon LEGO CMS page format (matching final_body.json structure)
 * Port of ui/lego_converter.py → TypeScript
 */

let idCounter = 0;
function genId(): string {
  return `w_${Date.now().toString(36)}_${(idCounter++).toString(36)}`;
}
function genUuid(): string {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}

// Draft.js content block format
function draftBlock(text: string): string {
  const key = Math.random().toString(36).substring(2, 7);
  const block = {
    blocks: [{ key, text, type: "unstyled", depth: 0, inlineStyleRanges: [], entityRanges: [], data: {} }],
    entityMap: {},
  };
  return JSON.stringify(block);
}

function cleanMarkdown(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/__(.+?)__/g, "$1")
    .replace(/(?<!\w)\*(.+?)\*(?!\w)/g, "$1")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^[-*]\s+/gm, "")
    .trim();
}

function baseContainer(widgets: unknown[] = [], overrides: Record<string, unknown> = {}): Record<string, unknown> {
  const container: Record<string, unknown> = {
    borderRadiusDesktop: "none", borderRadiusTablet: "desktop", borderRadiusMobileportrait: "tablet", borderRadiusMobilelandscape: "tablet",
    widthDesktop: 12, widthTablet: 12, widthMobileportrait: 12, widthMobilelandscape: 12,
    imageOrVideoBg: "image", backgroundURL: "", videoBackgroundURL: "", secondaryVideoBackgroundURL: "", posterURL: "",
    videoAttrs: ["autoPlay", "muted", "loop", "playsInline"], videoCaptions: [],
    backgroundPosition: "center center", backgroundSize: "cover", backgroundRepeat: "no-repeat",
    hyphens: "manual", overflowWrap: "normal", wordBreak: "normal",
    elementId: "", cssClass: "", data: [], language: "default",
    deviceColumnsTablet: false, deviceColumnsMobileportrait: false, deviceColumnsMobilelandscape: false,
    horizontalAlignmentDesktop: "default", horizontalAlignmentTablet: "desktop", horizontalAlignmentMobileportrait: "tablet", horizontalAlignmentMobilelandscape: "tablet",
    verticalItemsAlignmentDesktop: "stretch", verticalItemsAlignmentTablet: "desktop", verticalItemsAlignmentMobileportrait: "tablet", verticalItemsAlignmentMobilelandscape: "tablet",
    verticalContentAlignmentDesktop: "flex-start", verticalContentAlignmentTablet: "desktop", verticalContentAlignmentMobileportrait: "tablet", verticalContentAlignmentMobilelandscape: "tablet",
    isFullHeight: false, hasMaxWidth: true,
    deviceAvailability: ["desktop", "tablet", "mobilePortrait"],
    isSticky: false, stickyPosition: "top",
    animateOnScrollType: "none", animateOnScrollDelay: "100", animateOnScrollDuration: "600",
    preventImageOptimization: false, inputDependency: false, inputDependencies: [], queryDependency: false, queryDependencies: [],
    borderWidthTopDesktop: "zero", borderWidthTopTablet: "desktop", borderWidthTopMobileportrait: "tablet", borderWidthTopMobilelandscape: "tablet",
    borderWidthLeftDesktop: "zero", borderWidthLeftTablet: "desktop", borderWidthLeftMobileportrait: "tablet", borderWidthLeftMobilelandscape: "tablet",
    borderWidthRightDesktop: "zero", borderWidthRightTablet: "desktop", borderWidthRightMobileportrait: "tablet", borderWidthRightMobilelandscape: "tablet",
    borderWidthBottomDesktop: "zero", borderWidthBottomTablet: "desktop", borderWidthBottomMobileportrait: "tablet", borderWidthBottomMobilelandscape: "tablet",
    paddingTopDesktop: "minibase", paddingTopTablet: "base", paddingTopMobileportrait: "tablet", paddingTopMobilelandscape: "tablet",
    paddingLeftDesktop: "xxlarge", paddingLeftTablet: "xsmall", paddingLeftMobileportrait: "tablet", paddingLeftMobilelandscape: "tablet",
    paddingRightDesktop: "xxlarge", paddingRightTablet: "xsmall", paddingRightMobileportrait: "tablet", paddingRightMobilelandscape: "tablet",
    paddingBottomDesktop: "minibase", paddingBottomTablet: "desktop", paddingBottomMobileportrait: "tablet", paddingBottomMobilelandscape: "tablet",
    hasWave: false, waveStyle: "style-1", waveColor: "white", flipWave: false, wavePlacement: "bottom",
    hasBoxShadow: false, boxShadowType: "light",
    isFluid: false, noWrap: false, isMobileRow: false,
    backgroundColor: "transparent", borderColor: "squid-ink", gradientAngle: "0deg",
    isSearchAnchor: false, searchAnchorText: "",
    hoverAnimation: "none", hoverSpeed: "normal",
    sellDesignSnippetClass: "", tabId: "", showTabOnLoad: false,
    widgetClassName: "Container",
    reusable: null, reusablePlaceholder: null,
    id: genId(), widgets,
    design: "Sell", uuid: genUuid(), legoVersion: "2",
  };
  Object.assign(container, overrides);
  return container;
}

function textWidget(text: string, fontSize = "small", color = "storm"): Record<string, unknown> {
  return {
    content: draftBlock(cleanMarkdown(text)),
    alignmentDesktop: "start", alignmentTablet: "desktop", alignmentMobileportrait: "tablet", alignmentMobilelandscape: "tablet",
    disableTranslatable: false,
    fontSizeDesktop: fontSize, fontSizeTablet: "desktop", fontSizeMobileportrait: "tablet", fontSizeMobilelandscape: "tablet",
    fontFamily: "ember", color, fontWeight: "normal",
    useTooltip: false, tooltipStyle: "light", tooltipContent: "",
    widgetClassName: "Text", reusable: null, reusablePlaceholder: null, id: genId(),
  };
}

function headingWidget(text: string, level = "1"): Record<string, unknown> {
  const fontSize = level === "1" ? "large" : level === "2" ? "medium" : "small";
  return {
    content: draftBlock(cleanMarkdown(text)),
    headingLevel: level,
    alignmentDesktop: "start", alignmentTablet: "desktop", alignmentMobileportrait: "tablet", alignmentMobilelandscape: "tablet",
    disableTranslatable: false,
    fontSizeDesktop: fontSize, fontSizeTablet: "desktop", fontSizeMobileportrait: "tablet", fontSizeMobilelandscape: "tablet",
    color: "squid-ink", fontFamily: "ember", fontWeight: "bold",
    useTooltip: false, tooltipStyle: "light", tooltipContent: "",
    widgetClassName: "Heading", reusable: null, reusablePlaceholder: null, id: genId(),
  };
}

/**
 * Convert a markdown article into LEGO Sell Design page JSON
 */
export function convertArticleToLegoPage(title: string, content: string, label = "跨境知识荟"): Record<string, unknown> {
  const containers: Record<string, unknown>[] = [];

  // 1. Label
  containers.push(baseContainer([textWidget(label, "xsmall", "squid-ink")], { paddingBottomDesktop: "xsmall" }));

  // 2. Title (H1)
  containers.push(baseContainer([headingWidget(title, "1")], { paddingTopDesktop: "zero", paddingBottomDesktop: "mini" }));

  // 3. Parse content into sections
  const lines = content.split("\n");
  let currentBlock: string[] = [];

  const flushBlock = () => {
    if (currentBlock.length === 0) return;
    const text = currentBlock.join("\n").trim();
    if (text) {
      containers.push(baseContainer([textWidget(text, "small", "storm")]));
    }
    currentBlock = [];
  };

  for (const line of lines) {
    if (line.startsWith("## ")) {
      flushBlock();
      const h2Text = line.replace(/^##\s+/, "").trim();
      containers.push(baseContainer([headingWidget(h2Text, "2")], { paddingTopDesktop: "base" }));
    } else if (line.startsWith("### ")) {
      flushBlock();
      const h3Text = line.replace(/^###\s+/, "").trim();
      containers.push(baseContainer([headingWidget(h3Text, "3")], { paddingTopDesktop: "mini" }));
    } else {
      currentBlock.push(line);
    }
  }
  flushBlock();

  // 4. Data source footer
  containers.push(baseContainer([textWidget("数据来源：亚马逊全球开店官方指南（gs.amazon.cn）", "xsmall", "storm")]));

  // 5. Remark
  const now = new Date();
  containers.push(baseContainer([textWidget(`备注：以上信息更新时间为${now.getFullYear()}年${now.getMonth() + 1}月，关注全球开店官网及时了解最新变化。`, "small", "storm")], { paddingTopDesktop: "base" }));

  // Wrap all in outer page container
  const outerRow = baseContainer(containers, {
    hasMaxWidth: true,
    paddingTopDesktop: "minibase",
    paddingLeftDesktop: "xxlarge",
    paddingRightDesktop: "xxlarge",
    paddingBottomDesktop: "minibase",
  });

  // Page-level wrapper (matches final_body.json top-level structure)
  const page = baseContainer([outerRow], {
    widthDesktop: 12,
    hasMaxWidth: true,
    paddingTopDesktop: "minibase",
    paddingLeftDesktop: "xxlarge",
    paddingRightDesktop: "xxlarge",
    paddingBottomDesktop: "minibase",
  });

  return page;
}
