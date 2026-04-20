(async () => {
  try {
    // ============================================================================
    // DYNAMIC-PAGE ACCESS: load all pages before touching children
    // ============================================================================
    await figma.loadAllPagesAsync();

    // ============================================================================
    // HELPER FUNCTIONS
    // ============================================================================

    function hsl(str) {
      const [h, s, l] = str
        .replace(/%/g, "")
        .split(/\s+/)
        .map(Number);
      const H = h / 360;
      const S = s / 100;
      const L = l / 100;
      if (S === 0) return { r: L, g: L, b: L };
      const h2r = (p, q, t) => {
        if (t < 0) t += 1;
        if (t > 1) t -= 1;
        if (t < 1 / 6) return p + (q - p) * 6 * t;
        if (t < 1 / 2) return q;
        if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
        return p;
      };
      const q = L < 0.5 ? L * (1 + S) : L + S - L * S;
      const p = 2 * L - q;
      return {
        r: h2r(p, q, H + 1 / 3),
        g: h2r(p, q, H),
        b: h2r(p, q, H - 1 / 3),
      };
    }

    // Helper functions for scoped variable lookups
    let themeCollections = {};
    let primitivesCollection;
    let scaleCollection;

    function findThemeVar(brand, tokenName) {
      const coll = themeCollections[brand];
      if (!coll) return null;
      return figma.variables.getLocalVariables().find(
        (v) => v.name === tokenName && v.variableCollectionId === coll.id
      );
    }

    function findPrimitiveVar(tokenName) {
      return figma.variables.getLocalVariables().find(
        (v) => v.name === tokenName && v.variableCollectionId === primitivesCollection.id
      );
    }

    function findScaleVar(tokenName) {
      return figma.variables.getLocalVariables().find(
        (v) => v.name === tokenName && v.variableCollectionId === scaleCollection.id
      );
    }

    // Bind a variable to a node's fill/stroke by creating a bound SOLID paint.
    // Figma's setBoundVariable is only for non-array props; arrays (fills,
    // strokes) need setBoundVariableForPaint on an individual paint object.
    function bindFillVar(node, variable) {
      if (!variable) return;
      const bound = figma.variables.setBoundVariableForPaint(
        { type: "SOLID", color: { r: 0, g: 0, b: 0 } },
        "color",
        variable
      );
      node.fills = [bound];
    }

    function bindStrokeVar(node, variable) {
      if (!variable) return;
      const bound = figma.variables.setBoundVariableForPaint(
        { type: "SOLID", color: { r: 0, g: 0, b: 0 } },
        "color",
        variable
      );
      node.strokes = [bound];
    }

    // ============================================================================
    // THEMES MAP — source of truth from src/themes/*.ts
    // ============================================================================
    const THEMES = {
      wepdf: {
        background: "0 0% 100%",
        foreground: "222 47% 11%",
        card: "0 0% 100%",
        "card-foreground": "222 47% 11%",
        popover: "0 0% 100%",
        "popover-foreground": "222 47% 11%",
        primary: "221 83% 53%",
        "primary-foreground": "210 40% 98%",
        secondary: "210 40% 96%",
        "secondary-foreground": "222 47% 11%",
        muted: "210 40% 96%",
        "muted-foreground": "215 16% 47%",
        accent: "160 84% 39%",
        "accent-foreground": "160 100% 9%",
        destructive: "0 84% 60%",
        "destructive-foreground": "0 0% 98%",
        border: "214 32% 91%",
        input: "214 32% 91%",
        ring: "221 83% 53%",
        "radius-base": 12,
      },
      "trip-sorted": {
        background: "0 0% 100%",
        foreground: "215 60% 12%",
        card: "0 0% 100%",
        "card-foreground": "215 60% 12%",
        popover: "0 0% 100%",
        "popover-foreground": "215 60% 12%",
        primary: "215 72% 24%",
        "primary-foreground": "200 100% 97%",
        secondary: "199 93% 65%",
        "secondary-foreground": "215 60% 12%",
        muted: "210 40% 96%",
        "muted-foreground": "215 16% 47%",
        accent: "37 92% 50%",
        "accent-foreground": "30 100% 10%",
        destructive: "0 84% 60%",
        "destructive-foreground": "0 0% 98%",
        border: "214 32% 91%",
        input: "214 32% 91%",
        ring: "215 72% 24%",
        "radius-base": 14,
      },
      checkin: {
        background: "0 0% 100%",
        foreground: "210 75% 8%",
        card: "0 0% 100%",
        "card-foreground": "210 75% 8%",
        popover: "0 0% 100%",
        "popover-foreground": "210 75% 8%",
        primary: "201 96% 40%",
        "primary-foreground": "0 0% 100%",
        secondary: "210 40% 96%",
        "secondary-foreground": "210 75% 8%",
        muted: "210 40% 96%",
        "muted-foreground": "215 16% 47%",
        accent: "38 92% 50%",
        "accent-foreground": "30 100% 10%",
        destructive: "0 84% 60%",
        "destructive-foreground": "0 0% 98%",
        border: "214 32% 91%",
        input: "214 32% 91%",
        ring: "201 96% 40%",
        "radius-base": 10,
      },
      topup: {
        background: "0 0% 100%",
        foreground: "20 50% 10%",
        card: "0 0% 100%",
        "card-foreground": "20 50% 10%",
        popover: "0 0% 100%",
        "popover-foreground": "20 50% 10%",
        primary: "22 96% 46%",
        "primary-foreground": "30 100% 98%",
        secondary: "20 20% 96%",
        "secondary-foreground": "20 50% 10%",
        muted: "20 20% 96%",
        "muted-foreground": "20 15% 40%",
        accent: "125 44% 33%",
        "accent-foreground": "120 60% 96%",
        destructive: "0 84% 60%",
        "destructive-foreground": "0 0% 98%",
        border: "20 15% 88%",
        input: "20 15% 88%",
        ring: "22 96% 46%",
        "radius-base": 16,
      },
      admin: {
        background: "240 10% 4%",
        foreground: "240 5% 96%",
        card: "240 10% 9%",
        "card-foreground": "240 5% 96%",
        popover: "240 9% 11%",
        "popover-foreground": "240 5% 96%",
        primary: "240 5% 96%",
        "primary-foreground": "240 10% 4%",
        secondary: "240 9% 11%",
        "secondary-foreground": "240 5% 96%",
        muted: "240 9% 11%",
        "muted-foreground": "240 4% 63%",
        accent: "221 83% 60%",
        "accent-foreground": "240 10% 4%",
        destructive: "0 72% 51%",
        "destructive-foreground": "0 0% 98%",
        border: "240 5% 15%",
        input: "240 5% 15%",
        ring: "221 83% 60%",
        "radius-base": 8,
      },
    };

    // ============================================================================
    // 1. Load Inter font variants
    // ============================================================================
    const fontNames = [
      { name: "Inter", style: "Regular" },
      { name: "Inter", style: "Medium" },
      { name: "Inter", style: "Semi Bold" },
      { name: "Inter", style: "Bold" },
    ];

    for (const font of fontNames) {
      try {
        await figma.loadFontAsync(font);
      } catch (e) {
        console.warn(`Could not load font: ${font.name} ${font.style}`);
      }
    }

    // ============================================================================
    // 2. Archive existing base page
    // ============================================================================
    const allPages = figma.root.children;
    const existingBasePage = allPages.find(
      (p) => p.name === "🏢 Sanjow Base"
    );
    if (existingBasePage) {
      existingBasePage.name = "📦 Archive · v0";
    }

    // ============================================================================
    // 3. Create or get pages
    // ============================================================================
    const pageNames = [
      "🌅 Cover",
      "🎨 Foundations",
      "🌈 Themes",
      "🧩 Components",
      "📝 Changelog",
    ];
    const pages = {};

    for (const pageName of pageNames) {
      let page = allPages.find((p) => p.name === pageName);
      if (!page) {
        page = figma.createPage();
        page.name = pageName;
      } else {
        // Clear existing children
        for (const child of page.children) {
          child.remove();
        }
      }
      pages[pageName] = page;
    }

    // ============================================================================
    // 4. Create or reset Variable Collections
    // ============================================================================

    // Clean up existing collections
    for (const collection of figma.variables.getLocalVariableCollections()) {
      if (
        [
          "🎯 Primitives",
          "🌈 Theme",
          "📐 Scale",
          "🌈 Theme · WePDF",
          "🌈 Theme · Trip Sorted",
          "🌈 Theme · Checkin",
          "🌈 Theme · Topup",
          "🌈 Theme · Admin",
        ].includes(collection.name)
      ) {
        figma.variables.deleteVariableCollection(collection);
      }
    }

    // 4a. PRIMITIVES collection
    primitivesCollection = figma.variables.createVariableCollection(
      "🎯 Primitives"
    );

    const primitiveVars = {
      "gray/0": hsl("0 0% 100%"),
      "gray/50": hsl("220 13% 98%"),
      "gray/100": hsl("220 13% 96%"),
      "gray/200": hsl("220 13% 91%"),
      "gray/300": hsl("220 12% 84%"),
      "gray/400": hsl("220 9% 67%"),
      "gray/500": hsl("220 9% 46%"),
      "gray/600": hsl("220 11% 36%"),
      "gray/700": hsl("220 13% 28%"),
      "gray/800": hsl("220 14% 15%"),
      "gray/900": hsl("220 14% 9%"),
      "gray/950": hsl("240 10% 6%"),
      "status/success": hsl("160 84% 39%"),
      "status/success-fg": hsl("160 100% 9%"),
      "status/warning": hsl("38 92% 50%"),
      "status/warning-fg": hsl("30 100% 10%"),
      "status/danger": hsl("0 84% 60%"),
      "status/danger-fg": hsl("0 0% 98%"),
      "status/info": hsl("201 96% 40%"),
      "status/info-fg": hsl("0 0% 100%"),
      "chrome/ink": hsl("240 10% 4%"),
      "chrome/surface": hsl("240 10% 9%"),
      "chrome/elevated": hsl("240 9% 11%"),
      "chrome/text": hsl("220 13% 96%"),
      "chrome/text-dim": hsl("220 9% 67%"),
    };

    for (const [name, color] of Object.entries(primitiveVars)) {
      const variable = figma.variables.createVariable(
        name,
        primitivesCollection,
        "COLOR"
      );
      variable.setValueForMode(
        primitivesCollection.defaultModeId,
        color
      );
    }

    // 4b. THEME collections (5 separate single-mode collections for Starter plan)
    const themeCollectionNames = {
      wepdf: "🌈 Theme · WePDF",
      "trip-sorted": "🌈 Theme · Trip Sorted",
      checkin: "🌈 Theme · Checkin",
      topup: "🌈 Theme · Topup",
      admin: "🌈 Theme · Admin",
    };

    const themeTokenNames = [
      "background",
      "foreground",
      "card",
      "card-foreground",
      "popover",
      "popover-foreground",
      "primary",
      "primary-foreground",
      "secondary",
      "secondary-foreground",
      "muted",
      "muted-foreground",
      "accent",
      "accent-foreground",
      "destructive",
      "destructive-foreground",
      "border",
      "input",
      "ring",
    ];

    // Create 5 separate collections (one per brand)
    for (const [brandKey, collectionName] of Object.entries(themeCollectionNames)) {
      const brandCollection = figma.variables.createVariableCollection(collectionName);

      // Create 19 color tokens
      for (const tokenName of themeTokenNames) {
        const variable = figma.variables.createVariable(
          tokenName,
          brandCollection,
          "COLOR"
        );

        const hslStr = THEMES[brandKey][tokenName];
        const color = hsl(hslStr);
        variable.setValueForMode(brandCollection.defaultModeId, color);
      }

      // Create radius/base FLOAT variable
      const radiusVariable = figma.variables.createVariable(
        "radius/base",
        brandCollection,
        "FLOAT"
      );
      radiusVariable.setValueForMode(
        brandCollection.defaultModeId,
        THEMES[brandKey]["radius-base"]
      );

      // Store reference for later lookup
      themeCollections[brandKey] = brandCollection;
    }

    // 4c. SCALE collection
    scaleCollection = figma.variables.createVariableCollection(
      "📐 Scale"
    );

    const spaceValues = {
      "space/0": 0,
      "space/0-5": 2,
      "space/1": 4,
      "space/2": 8,
      "space/3": 12,
      "space/4": 16,
      "space/5": 20,
      "space/6": 24,
      "space/8": 32,
      "space/10": 40,
      "space/12": 48,
      "space/16": 64,
      "space/20": 80,
      "space/24": 96,
      "space/32": 128,
    };

    for (const [name, value] of Object.entries(spaceValues)) {
      const variable = figma.variables.createVariable(
        name,
        scaleCollection,
        "FLOAT"
      );
      variable.setValueForMode(scaleCollection.defaultModeId, value);
    }

    const radiusValues = {
      "radius/sm": 4,
      "radius/md": 8,
      "radius/lg": 12,
      "radius/xl": 16,
      "radius/2xl": 24,
      "radius/pill": 9999,
    };

    for (const [name, value] of Object.entries(radiusValues)) {
      const variable = figma.variables.createVariable(
        name,
        scaleCollection,
        "FLOAT"
      );
      variable.setValueForMode(scaleCollection.defaultModeId, value);
    }

    // ============================================================================
    // 5. Populate 🎨 Foundations page
    // ============================================================================
    const foundationsPage = pages["🎨 Foundations"];
    await figma.setCurrentPageAsync(foundationsPage);

    // Title
    const titleFrame = figma.createFrame();
    titleFrame.name = "Foundations";
    titleFrame.x = 40;
    titleFrame.y = 40;
    titleFrame.width = 1200;
    titleFrame.height = 60;
    titleFrame.layoutMode = "VERTICAL";
    titleFrame.verticalPadding = 10;
    titleFrame.horizontalPadding = 16;
    titleFrame.fills = [{ type: "SOLID", color: { r: 0.97, g: 0.97, b: 0.98 } }];

    const titleText = figma.createText();
    titleText.characters = "Foundations";
    titleText.fontSize = 48;
    titleText.fontName = { family: "Inter", style: "Bold" };
    titleText.fills = [{ type: "SOLID", color: { r: 0.05, g: 0.05, b: 0.06 } }];
    titleFrame.appendChild(titleText);
    foundationsPage.appendChild(titleFrame);

    // Grayscale swatches (12 tiles)
    const grayTitles = [
      "0",
      "50",
      "100",
      "200",
      "300",
      "400",
      "500",
      "600",
      "700",
      "800",
      "900",
      "950",
    ];
    const grayContainer = figma.createFrame();
    grayContainer.name = "Grayscale Swatches";
    grayContainer.x = 40;
    grayContainer.y = 140;
    grayContainer.layoutMode = "HORIZONTAL";
    grayContainer.itemSpacing = 8;
    grayContainer.fills = [];

    for (const title of grayTitles) {
      const tile = figma.createRectangle();
      tile.name = `gray/${title}`;
      tile.width = 80;
      tile.height = 80;
      tile.cornerRadius = 8;
      const variable = findPrimitiveVar(`gray/${title}`);
      if (variable) {
        bindFillVar(tile, variable);
      }
      grayContainer.appendChild(tile);
    }
    foundationsPage.appendChild(grayContainer);

    // Status swatches (8 tiles)
    const statusTitles = [
      "status/success",
      "status/success-fg",
      "status/warning",
      "status/warning-fg",
      "status/danger",
      "status/danger-fg",
      "status/info",
      "status/info-fg",
    ];
    const statusContainer = figma.createFrame();
    statusContainer.name = "Status Swatches";
    statusContainer.x = 40;
    statusContainer.y = 260;
    statusContainer.layoutMode = "HORIZONTAL";
    statusContainer.itemSpacing = 8;
    statusContainer.fills = [];

    for (const title of statusTitles) {
      const tile = figma.createRectangle();
      tile.name = title;
      tile.width = 80;
      tile.height = 80;
      tile.cornerRadius = 8;
      const variable = findPrimitiveVar(title);
      if (variable) {
        bindFillVar(tile, variable);
      }
      statusContainer.appendChild(tile);
    }
    foundationsPage.appendChild(statusContainer);

    // Typography specimens
    const typogContainer = figma.createFrame();
    typogContainer.name = "Typography";
    typogContainer.x = 40;
    typogContainer.y = 380;
    typogContainer.layoutMode = "VERTICAL";
    typogContainer.itemSpacing = 16;
    typogContainer.fills = [];

    const typogSpecs = [
      { name: "Display", size: 48, weight: "Bold", text: "Display 48px Bold" },
      { name: "H1", size: 36, weight: "Semi Bold", text: "H1 36px Semi Bold" },
      { name: "H2", size: 28, weight: "Semi Bold", text: "H2 28px Semi Bold" },
      { name: "H3", size: 20, weight: "Semi Bold", text: "H3 20px Semi Bold" },
      { name: "Body", size: 16, weight: "Regular", text: "Body 16px Regular" },
      { name: "Small", size: 13, weight: "Regular", text: "Small 13px Regular" },
      { name: "Micro", size: 11, weight: "Medium", text: "Micro 11px Medium" },
    ];

    for (const spec of typogSpecs) {
      const text = figma.createText();
      text.characters = spec.text;
      text.fontSize = spec.size;
      text.fontName = { family: "Inter", style: spec.weight };
      text.fills = [{ type: "SOLID", color: { r: 0.05, g: 0.05, b: 0.06 } }];
      typogContainer.appendChild(text);
    }
    foundationsPage.appendChild(typogContainer);

    // Spacing scale bars (12 items)
    const spacingContainer = figma.createFrame();
    spacingContainer.name = "Spacing Scale";
    spacingContainer.x = 40;
    spacingContainer.y = 780;
    spacingContainer.layoutMode = "VERTICAL";
    spacingContainer.itemSpacing = 12;
    spacingContainer.fills = [];

    const spacingLabels = [
      "0",
      "0.5",
      "1",
      "2",
      "3",
      "4",
      "5",
      "6",
      "8",
      "10",
      "12",
      "16",
    ];
    const spacingPixels = [0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64];

    for (let i = 0; i < spacingLabels.length; i++) {
      const row = figma.createFrame();
      row.layoutMode = "HORIZONTAL";
      row.itemSpacing = 12;
      row.fills = [];

      const label = figma.createText();
      label.characters = `space/${spacingLabels[i]}`;
      label.fontSize = 12;
      label.fontName = { family: "Inter", style: "Regular" };
      label.fills = [{ type: "SOLID", color: { r: 0.3, g: 0.3, b: 0.3 } }];
      row.appendChild(label);

      const bar = figma.createRectangle();
      bar.width = spacingPixels[i];
      bar.height = 20;
      bar.fills = [{ type: "SOLID", color: { r: 0.65, g: 0.65, b: 0.65 } }];
      bar.cornerRadius = 4;
      row.appendChild(bar);

      spacingContainer.appendChild(row);
    }
    foundationsPage.appendChild(spacingContainer);

    // Radius demo tiles (6 items)
    const radiusContainer = figma.createFrame();
    radiusContainer.name = "Border Radius";
    radiusContainer.x = 1300;
    radiusContainer.y = 140;
    radiusContainer.layoutMode = "HORIZONTAL";
    radiusContainer.itemSpacing = 16;
    radiusContainer.fills = [];

    const radiusValues2 = [
      { name: "sm", value: 4 },
      { name: "md", value: 8 },
      { name: "lg", value: 12 },
      { name: "xl", value: 16 },
      { name: "2xl", value: 24 },
      { name: "pill", value: 9999 },
    ];

    for (const r of radiusValues2) {
      const tile = figma.createRectangle();
      tile.name = `radius/${r.name}`;
      tile.width = 80;
      tile.height = 80;
      tile.cornerRadius = r.value;
      tile.fills = [{ type: "SOLID", color: { r: 0.2, g: 0.6, b: 0.8 } }];
      radiusContainer.appendChild(tile);
    }
    foundationsPage.appendChild(radiusContainer);

    // Elevation demo (5 shadows)
    const elevationContainer = figma.createFrame();
    elevationContainer.name = "Elevation / Shadows";
    elevationContainer.x = 1300;
    elevationContainer.y = 280;
    elevationContainer.layoutMode = "VERTICAL";
    elevationContainer.itemSpacing = 24;
    elevationContainer.fills = [];

    const shadowLevels = [
      { name: "xs", blur: 2, spread: 0, offset: 1 },
      { name: "sm", blur: 3, spread: 0, offset: 1 },
      { name: "md", blur: 6, spread: -1, offset: 4 },
      { name: "lg", blur: 15, spread: -3, offset: 10 },
      { name: "xl", blur: 25, spread: -5, offset: 20 },
    ];

    for (const shadow of shadowLevels) {
      const tile = figma.createRectangle();
      tile.name = `shadow-${shadow.name}`;
      tile.width = 120;
      tile.height = 60;
      tile.cornerRadius = 8;
      tile.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
      tile.strokes = [{ type: "SOLID", color: { r: 0.9, g: 0.9, b: 0.9 } }];
      tile.strokeWeight = 1;
      tile.effects = [
        {
          type: "DROP_SHADOW",
          visible: true,
          color: { r: 0, g: 0, b: 0, a: 0.1 },
          offset: { x: 0, y: shadow.offset },
          blur: shadow.blur,
          spread: shadow.spread,
        },
      ];
      elevationContainer.appendChild(tile);
    }
    foundationsPage.appendChild(elevationContainer);

    // ============================================================================
    // 6. Populate 🌈 Themes page (5 brand columns)
    // ============================================================================
    const themesPage = pages["🌈 Themes"];
    await figma.setCurrentPageAsync(themesPage);

    const brandInfo = {
      wepdf: {
        name: "WePDF",
        tagline: "The PDF toolkit that never surprises you.",
        repos: ["pdf-ai"],
      },
      "trip-sorted": {
        name: "Trip Sorted",
        tagline: "Travel, sorted.",
        repos: ["fast-track-ai", "new-fast-track", "travel-dashboard"],
      },
      checkin: {
        name: "Airport Check-in",
        tagline: "Check in. Print. Board. That's it.",
        repos: ["checkin-ai", "airport-checkin", "new-airport-checkin"],
      },
      topup: {
        name: "TopUp",
        tagline: "Credit home in 30 seconds. No subscription. Never.",
        repos: ["top-up", "topup"],
      },
      admin: {
        name: "Sanjow Admin",
        tagline: "Internal dashboard chrome.",
        repos: ["back-office", "global-dashboard", "monorepo"],
      },
    };

    const themesContainer = figma.createFrame();
    themesContainer.name = "Themes Overview";
    themesContainer.x = 40;
    themesContainer.y = 40;
    themesContainer.layoutMode = "HORIZONTAL";
    themesContainer.itemSpacing = 32;
    themesContainer.fills = [];

    for (const [brandKey, brandData] of Object.entries(brandInfo)) {
      const brandColumn = figma.createFrame();
      brandColumn.name = brandKey;
      brandColumn.width = 240;
      brandColumn.layoutMode = "VERTICAL";
      brandColumn.itemSpacing = 12;
      brandColumn.verticalPadding = 16;
      brandColumn.horizontalPadding = 12;
      brandColumn.fills = [
        { type: "SOLID", color: { r: 0.97, g: 0.97, b: 0.98 } },
      ];
      brandColumn.cornerRadius = 12;

      // Brand name
      const brandTitle = figma.createText();
      brandTitle.characters = brandData.name;
      brandTitle.fontSize = 18;
      brandTitle.fontName = { family: "Inter", style: "Bold" };
      const fgVar = findThemeVar(brandKey, "foreground");
      if (fgVar) {
        brandTitle.fills = [
          {
            type: "VARIABLE",
            boundVariables: {
              color: fgVar,
            },
          },
        ];
      }
      brandColumn.appendChild(brandTitle);

      // Tagline
      const taglineText = figma.createText();
      taglineText.characters = brandData.tagline;
      taglineText.fontSize = 12;
      taglineText.fontName = { family: "Inter", style: "Regular" };
      const mutedFgVar = findThemeVar(brandKey, "muted-foreground");
      if (mutedFgVar) {
        taglineText.fills = [
          {
            type: "VARIABLE",
            boundVariables: {
              color: mutedFgVar,
            },
          },
        ];
      }
      brandColumn.appendChild(taglineText);

      // Repos list
      const reposText = figma.createText();
      reposText.characters = `Repos: ${brandData.repos.join(", ")}`;
      reposText.fontSize = 10;
      reposText.fontName = { family: "Inter", style: "Regular" };
      if (mutedFgVar) {
        reposText.fills = [
          {
            type: "VARIABLE",
            boundVariables: {
              color: mutedFgVar,
            },
          },
        ];
      }
      brandColumn.appendChild(reposText);

      // Swatches (5 color swatches: primary, accent, secondary, muted, border)
      const swatchNames = ["primary", "accent", "secondary", "muted", "border"];
      const swatchRow = figma.createFrame();
      swatchRow.layoutMode = "HORIZONTAL";
      swatchRow.itemSpacing = 6;
      swatchRow.fills = [];

      for (const swatchName of swatchNames) {
        const swatch = figma.createRectangle();
        swatch.name = swatchName;
        swatch.width = 40;
        swatch.height = 40;
        swatch.cornerRadius = 6;
        const colorVar = findThemeVar(brandKey, swatchName);
        if (colorVar) {
          bindFillVar(swatch, colorVar);
        }
        swatchRow.appendChild(swatch);
      }
      brandColumn.appendChild(swatchRow);

      // Mini button preview (bound to primary)
      const buttonPreview = figma.createRectangle();
      buttonPreview.name = "Button Preview";
      buttonPreview.width = 100;
      buttonPreview.height = 36;
      buttonPreview.cornerRadius = 6;
      const primaryVar = findThemeVar(brandKey, "primary");
      if (primaryVar) {
        bindFillVar(buttonPreview, primaryVar);
      }

      const buttonText = figma.createText();
      buttonText.characters = "Button";
      buttonText.fontSize = 12;
      buttonText.fontName = { family: "Inter", style: "Medium" };
      const primaryFgVar = findThemeVar(brandKey, "primary-foreground");
      if (primaryFgVar) {
        buttonText.fills = [
          {
            type: "VARIABLE",
            boundVariables: {
              color: primaryFgVar,
            },
          },
        ];
      }
      buttonPreview.appendChild(buttonText);
      brandColumn.appendChild(buttonPreview);

      // Card preview
      const cardPreview = figma.createFrame();
      cardPreview.name = "Card Preview";
      cardPreview.width = 200;
      cardPreview.height = 80;
      cardPreview.layoutMode = "VERTICAL";
      cardPreview.verticalPadding = 12;
      cardPreview.horizontalPadding = 12;
      cardPreview.itemSpacing = 8;
      cardPreview.cornerRadius = 8;

      const cardVar = findThemeVar(brandKey, "card");
      if (cardVar) {
        bindFillVar(cardPreview, cardVar);
      }

      const cardBorder = findThemeVar(brandKey, "border");
      if (cardBorder) {
        bindStrokeVar(cardPreview, cardBorder);
      }
      cardPreview.strokeWeight = 1;

      const cardTitle = figma.createText();
      cardTitle.characters = "Card Title";
      cardTitle.fontSize = 14;
      cardTitle.fontName = { family: "Inter", style: "Semi Bold" };
      const cardFgVar = findThemeVar(brandKey, "card-foreground");
      if (cardFgVar) {
        cardTitle.fills = [
          {
            type: "VARIABLE",
            boundVariables: {
              color: cardFgVar,
            },
          },
        ];
      }
      cardPreview.appendChild(cardTitle);

      const cardDesc = figma.createText();
      cardDesc.characters = "Description text";
      cardDesc.fontSize = 11;
      cardDesc.fontName = { family: "Inter", style: "Regular" };
      const cardMutedVar = findThemeVar(brandKey, "muted-foreground");
      if (cardMutedVar) {
        cardDesc.fills = [
          {
            type: "VARIABLE",
            boundVariables: {
              color: cardMutedVar,
            },
          },
        ];
      }
      cardPreview.appendChild(cardDesc);

      brandColumn.appendChild(cardPreview);
      themesContainer.appendChild(brandColumn);
    }
    themesPage.appendChild(themesContainer);

    // ============================================================================
    // 7. Populate 🧩 Components page (4 component sets)
    // ============================================================================
    const componentsPage = pages["🧩 Components"];
    await figma.setCurrentPageAsync(componentsPage);

    // Component specs
    const componentSpecs = {
      button: {
        name: "Button",
        variants: {
          variant: ["primary", "secondary", "accent", "outline", "ghost", "destructive", "link"],
          size: ["sm", "md", "lg"],
          fullWidth: ["false", "true"],
        },
        heights: { sm: 32, md: 40, lg: 48 },
        paddings: { sm: 12, md: 16, lg: 20 },
      },
      input: {
        name: "Input",
        variants: { invalid: ["false", "true"] },
        height: 40,
        width: 280,
        padding: 12,
      },
      card: {
        name: "Card",
        variants: {},
        width: 300,
        height: 180,
      },
      badge: {
        name: "Badge",
        variants: {
          variant: [
            "default",
            "secondary",
            "accent",
            "outline",
            "success",
            "warning",
            "danger",
            "info",
          ],
        },
      },
    };

    // Create Button component set
    const buttonComponents = [];
    const buttonComponentSet = figma.createComponentSet();
    buttonComponentSet.name = "Button";

    for (const variant of componentSpecs.button.variants.variant) {
      for (const size of componentSpecs.button.variants.size) {
        for (const fullWidth of componentSpecs.button.variants.fullWidth) {
          const component = figma.createComponent();
          component.name = `Button/${variant}/${size}/${fullWidth}`;
          component.width = fullWidth === "true" ? 200 : 100;
          component.height = componentSpecs.button.heights[size];
          component.layoutMode = "HORIZONTAL";
          component.primaryAxisAlignItems = "CENTER";
          component.counterAxisAlignItems = "CENTER";
          component.verticalPadding = 8;
          component.horizontalPadding =
            componentSpecs.button.paddings[size];
          component.cornerRadius = 6;

          // Add variant properties
          component.addComponentProperty("variant", "VARIANT", variant);
          component.addComponentProperty("size", "VARIANT", size);
          component.addComponentProperty(
            "fullWidth",
            "VARIANT",
            fullWidth === "true"
          );

          // Set fill based on variant
          let fillVar = "primary";
          if (variant === "secondary") fillVar = "secondary";
          else if (variant === "accent") fillVar = "accent";
          else if (variant === "outline") fillVar = "border";
          else if (variant === "ghost") fillVar = "muted";
          else if (variant === "destructive") fillVar = "destructive";
          else if (variant === "link") fillVar = "primary";

          if (
            variant !== "outline" &&
            variant !== "ghost" &&
            variant !== "link"
          ) {
            const fillColorVar = findThemeVar("wepdf", fillVar);
            if (fillColorVar) {
              bindFillVar(component, fillColorVar);
            }
          } else if (variant === "outline") {
            component.fills = [];
            const borderVar = findThemeVar("wepdf", "border");
            if (borderVar) {
              bindStrokeVar(component, borderVar);
            }
            component.strokeWeight = 1;
          } else {
            component.fills = [];
          }

          // Add text
          const buttonText = figma.createText();
          buttonText.characters = "Button";
          buttonText.fontSize = 14;
          buttonText.fontName = { family: "Inter", style: "Medium" };

          let textVar = "primary-foreground";
          if (
            variant === "outline" ||
            variant === "ghost" ||
            variant === "link"
          ) {
            textVar = "primary";
          } else if (variant === "secondary") {
            textVar = "secondary-foreground";
          } else if (variant === "accent") {
            textVar = "accent-foreground";
          } else if (variant === "destructive") {
            textVar = "destructive-foreground";
          }

          const textVar2 = findThemeVar("wepdf", textVar);
          if (textVar2) {
            bindFillVar(buttonText, textVar2);
          }

          component.appendChild(buttonText);
          buttonComponents.push(component);
          buttonComponentSet.appendChild(component);
        }
      }
    }
    componentsPage.appendChild(buttonComponentSet);

    // Create Input component
    const inputComponent = figma.createComponent();
    inputComponent.name = "Input";
    inputComponent.width = componentSpecs.input.width;
    inputComponent.height = componentSpecs.input.height;
    inputComponent.cornerRadius = 8;
    inputComponent.layoutMode = "HORIZONTAL";
    inputComponent.verticalPadding = componentSpecs.input.padding;
    inputComponent.horizontalPadding = componentSpecs.input.padding;

    const inputVar = findThemeVar("wepdf", "input");
    if (inputVar) {
      bindFillVar(inputComponent, inputVar);
    }

    const borderVar = findThemeVar("wepdf", "border");
    if (borderVar) {
      bindStrokeVar(inputComponent, borderVar);
    }
    inputComponent.strokeWeight = 1;

    const inputText = figma.createText();
    inputText.characters = "Placeholder text...";
    inputText.fontSize = 14;
    inputText.fontName = { family: "Inter", style: "Regular" };
    const mutedVar = findThemeVar("wepdf", "muted-foreground");
    if (mutedVar) {
      bindFillVar(inputText, mutedVar);
    }
    inputComponent.appendChild(inputText);
    componentsPage.appendChild(inputComponent);

    // Create Card component
    const cardComponent = figma.createComponent();
    cardComponent.name = "Card";
    cardComponent.width = componentSpecs.card.width;
    cardComponent.height = componentSpecs.card.height;
    cardComponent.layoutMode = "VERTICAL";
    cardComponent.verticalPadding = 16;
    cardComponent.horizontalPadding = 16;
    cardComponent.itemSpacing = 12;
    cardComponent.cornerRadius = 8;

    const cardFillVar = findThemeVar("wepdf", "card");
    if (cardFillVar) {
      bindFillVar(cardComponent, cardFillVar);
    }

    const cardBorderVar = findThemeVar("wepdf", "border");
    if (cardBorderVar) {
      bindStrokeVar(cardComponent, cardBorderVar);
    }
    cardComponent.strokeWeight = 1;

    // Card header
    const cardHeader = figma.createFrame();
    cardHeader.layoutMode = "VERTICAL";
    cardHeader.itemSpacing = 4;
    cardHeader.fills = [];

    const cardHeaderTitle = figma.createText();
    cardHeaderTitle.characters = "Card Title";
    cardHeaderTitle.fontSize = 16;
    cardHeaderTitle.fontName = { family: "Inter", style: "Semi Bold" };
    const cardFgVar = findThemeVar("wepdf", "card-foreground");
    if (cardFgVar) {
      bindFillVar(cardHeaderTitle, cardFgVar);
    }
    cardHeader.appendChild(cardHeaderTitle);

    const cardHeaderDesc = figma.createText();
    cardHeaderDesc.characters = "Card description";
    cardHeaderDesc.fontSize = 12;
    cardHeaderDesc.fontName = { family: "Inter", style: "Regular" };
    const cardHeaderDescVar = findThemeVar("wepdf", "muted-foreground");
    if (cardHeaderDescVar) {
      bindFillVar(cardHeaderDesc, cardHeaderDescVar);
    }
    cardHeader.appendChild(cardHeaderDesc);
    cardComponent.appendChild(cardHeader);

    // Card content
    const cardContent = figma.createText();
    cardContent.characters = "Card content goes here...";
    cardContent.fontSize = 13;
    cardContent.fontName = { family: "Inter", style: "Regular" };
    if (cardFgVar) {
      bindFillVar(cardContent, cardFgVar);
    }
    cardComponent.appendChild(cardContent);
    componentsPage.appendChild(cardComponent);

    // Create Badge component set
    const badgeComponentSet = figma.createComponentSet();
    badgeComponentSet.name = "Badge";

    for (const badgeVariant of componentSpecs.badge.variants.variant) {
      const badge = figma.createComponent();
      badge.name = `Badge/${badgeVariant}`;
      badge.width = 100;
      badge.height = 28;
      badge.layoutMode = "HORIZONTAL";
      badge.primaryAxisAlignItems = "CENTER";
      badge.counterAxisAlignItems = "CENTER";
      badge.verticalPadding = 4;
      badge.horizontalPadding = 12;
      badge.cornerRadius = 9999;
      badge.addComponentProperty("variant", "VARIANT", badgeVariant);

      let badgeFillVar = "primary";
      let badgeTextVar = "primary-foreground";

      if (badgeVariant === "secondary") {
        badgeFillVar = "secondary";
        badgeTextVar = "secondary-foreground";
      } else if (badgeVariant === "accent") {
        badgeFillVar = "accent";
        badgeTextVar = "accent-foreground";
      } else if (badgeVariant === "outline") {
        badgeFillVar = "background";
        badgeTextVar = "foreground";
      } else if (badgeVariant === "success") {
        badgeFillVar = "status/success";
        badgeTextVar = "status/success-fg";
      } else if (badgeVariant === "warning") {
        badgeFillVar = "status/warning";
        badgeTextVar = "status/warning-fg";
      } else if (badgeVariant === "danger") {
        badgeFillVar = "status/danger";
        badgeTextVar = "status/danger-fg";
      } else if (badgeVariant === "info") {
        badgeFillVar = "status/info";
        badgeTextVar = "status/info-fg";
      }

      let badgeFill;
      if (badgeFillVar.startsWith("status/")) {
        badgeFill = findPrimitiveVar(badgeFillVar);
      } else {
        badgeFill = findThemeVar("wepdf", badgeFillVar);
      }
      if (badgeFill) {
        bindFillVar(badge, badgeFill);
      }

      if (badgeVariant === "outline") {
        const badgeBorder = findThemeVar("wepdf", "border");
        if (badgeBorder) {
          bindStrokeVar(badge, badgeBorder);
        }
        badge.strokeWeight = 1;
      }

      const badgeText = figma.createText();
      badgeText.characters = badgeVariant;
      badgeText.fontSize = 12;
      badgeText.fontName = { family: "Inter", style: "Medium" };
      let badgeTextVarObj;
      if (badgeTextVar.startsWith("status/")) {
        badgeTextVarObj = findPrimitiveVar(badgeTextVar);
      } else {
        badgeTextVarObj = findThemeVar("wepdf", badgeTextVar);
      }
      if (badgeTextVarObj) {
        bindFillVar(badgeText, badgeTextVarObj);
      }

      badge.appendChild(badgeText);
      badgeComponentSet.appendChild(badge);
    }
    componentsPage.appendChild(badgeComponentSet);

    // ============================================================================
    // 8. Populate 🌅 Cover page
    // ============================================================================
    const coverPage = pages["🌅 Cover"];
    await figma.setCurrentPageAsync(coverPage);

    // Dark background frame
    const coverFrame = figma.createFrame();
    coverFrame.name = "Cover";
    coverFrame.width = 1920;
    coverFrame.height = 1080;
    coverFrame.fills = [{ type: "SOLID", color: { r: 0.05, g: 0.05, b: 0.06 } }];
    coverFrame.layoutMode = "VERTICAL";
    coverFrame.primaryAxisAlignItems = "CENTER";
    coverFrame.counterAxisAlignItems = "CENTER";
    coverFrame.itemSpacing = 24;

    // Main title
    const coverTitle = figma.createText();
    coverTitle.characters = "Sanjow Design System";
    coverTitle.fontSize = 72;
    coverTitle.fontName = { family: "Inter", style: "Bold" };
    coverTitle.fills = [{ type: "SOLID", color: { r: 0.97, g: 0.97, b: 0.98 } }];
    coverFrame.appendChild(coverTitle);

    // Version and date
    const coverMeta = figma.createFrame();
    coverMeta.layoutMode = "HORIZONTAL";
    coverMeta.itemSpacing = 32;
    coverMeta.fills = [];

    const versionText = figma.createText();
    versionText.characters = "v0.1.0";
    versionText.fontSize = 24;
    versionText.fontName = { family: "Inter", style: "Semi Bold" };
    versionText.fills = [{ type: "SOLID", color: { r: 0.7, g: 0.7, b: 0.7 } }];
    coverMeta.appendChild(versionText);

    const dateText = figma.createText();
    dateText.characters = "April 2026";
    dateText.fontSize = 24;
    dateText.fontName = { family: "Inter", style: "Semi Bold" };
    dateText.fills = [{ type: "SOLID", color: { r: 0.7, g: 0.7, b: 0.7 } }];
    coverMeta.appendChild(dateText);

    coverFrame.appendChild(coverMeta);

    // Brand tiles grid (5 columns)
    const brandTilesGrid = figma.createFrame();
    brandTilesGrid.layoutMode = "HORIZONTAL";
    brandTilesGrid.itemSpacing = 20;
    brandTilesGrid.fills = [];

    for (const [brandKey, _] of Object.entries(brandInfo)) {
      const tile = figma.createFrame();
      tile.name = `brand-${brandKey}`;
      tile.width = 200;
      tile.height = 140;
      tile.layoutMode = "VERTICAL";
      tile.verticalPadding = 16;
      tile.horizontalPadding = 16;
      tile.cornerRadius = 12;
      tile.itemSpacing = 8;

      // Brand name on tile
      const tileName = figma.createText();
      tileName.characters = brandInfo[brandKey].name;
      tileName.fontSize = 14;
      tileName.fontName = { family: "Inter", style: "Bold" };
      const tileFgVar = findThemeVar(brandKey, "foreground");
      if (tileFgVar) {
        bindFillVar(tileName, tileFgVar);
      }
      tile.appendChild(tileName);

      // Bind card background
      const cardVar2 = findThemeVar(brandKey, "card");
      if (cardVar2) {
        bindFillVar(tile, cardVar2);
      }

      // Color swatches on tile
      const tileSwatches = figma.createFrame();
      tileSwatches.layoutMode = "HORIZONTAL";
      tileSwatches.itemSpacing = 4;
      tileSwatches.fills = [];

      for (const swatchColor of ["primary", "accent", "secondary"]) {
        const swatch = figma.createRectangle();
        swatch.width = 30;
        swatch.height = 30;
        swatch.cornerRadius = 4;
        const swatchVar = findThemeVar(brandKey, swatchColor);
        if (swatchVar) {
          bindFillVar(swatch, swatchVar);
        }
        tileSwatches.appendChild(swatch);
      }
      tile.appendChild(tileSwatches);

      brandTilesGrid.appendChild(tile);
    }
    coverFrame.appendChild(brandTilesGrid);

    // Legend
    const legend = figma.createText();
    legend.characters = "Synced from @sanjow/design-system npm package";
    legend.fontSize = 14;
    legend.fontName = { family: "Inter", style: "Regular" };
    legend.fills = [{ type: "SOLID", color: { r: 0.6, g: 0.6, b: 0.6 } }];
    coverFrame.appendChild(legend);

    coverPage.appendChild(coverFrame);

    // ============================================================================
    // 9. Populate 📝 Changelog page
    // ============================================================================
    const changelogPage = pages["📝 Changelog"];
    await figma.setCurrentPageAsync(changelogPage);

    const changelogText = figma.createText();
    changelogText.characters =
      "v0.1.0 · 2026-04-20\n- Mirror of @sanjow/design-system package\n- 7 variable collections: Primitives, 5 Theme collections (1 mode each), Scale\n- Foundations, Themes, Components, Cover pages";
    changelogText.fontSize = 16;
    changelogText.fontName = { family: "Inter", style: "Regular" };
    changelogText.fills = [{ type: "SOLID", color: { r: 0.05, g: 0.05, b: 0.06 } }];
    changelogText.x = 40;
    changelogText.y = 40;
    changelogPage.appendChild(changelogText);

    // ============================================================================
    // 10. Summary notification
    // ============================================================================
    const summary = `✓ Sanjow Design System v0.1.0 synced to Figma
✓ 7 Variable Collections: Primitives, 5 Theme Collections (1 mode each), Scale
✓ 5 Pages: Cover, Foundations, Themes, Components, Changelog
✓ 4 Component Sets: Button (7×3×2), Input, Card, Badge (8 variants)
✓ Idempotent script — safe to re-run`;

    figma.notify(summary);
    figma.closePlugin("Sanjow DS synced");
    return summary;
  } catch (error) {
    figma.notify(`Error: ${error.message}`);
    console.error(error);
    figma.closePlugin(`Error: ${error.message}`);
    throw error;
  }
})();
