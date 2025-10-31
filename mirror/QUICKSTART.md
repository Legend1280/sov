# Mirror v2 Quick Start Guide

**Author:** Brady Simmons  
**Copyright:** © 2025 Sovereignty Foundation. All rights reserved.

---

## 🚀 Get Started in 3 Steps

### Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/Legend1280/sov.git
cd sov/mirror

# Install dependencies
npm install
# or
pnpm install
```

### Step 2: Start Development Server

```bash
npm run dev
# or
pnpm dev
```

The server will start on `http://localhost:5173`

### Step 3: Open in Browser

Open your browser to:
```
http://localhost:5173
```

You should see the **DexaBooks** app with:
- ✅ Header with "Upload" button
- ✅ Navigator with Financial section
- ✅ Main viewport with dashboard

---

## 📁 Project Structure

```
mirror/
├── client/
│   └── src/
│       ├── apps/                    # App schemas (JSON)
│       │   ├── dexabooks/
│       │   │   ├── app.json        # App manifest
│       │   │   ├── header.json     # Header layout
│       │   │   ├── navigator.json  # Navigator layout
│       │   │   └── main.json       # Main viewport layout
│       │   └── sage/               # SAGE app schemas
│       ├── components/
│       │   ├── core/               # Core components
│       │   │   ├── AppContainer.tsx
│       │   │   ├── Renderer.tsx
│       │   │   ├── Text.tsx
│       │   │   ├── NavigatorSection.tsx
│       │   │   └── NavigatorItem.tsx
│       │   └── layout/             # Layout containers
│       │       ├── Grid.tsx
│       │       ├── Stack.tsx
│       │       ├── Tabs.tsx
│       │       └── Split.tsx
│       ├── core/                   # Core infrastructure
│       │   ├── EventBus.ts
│       │   ├── DataContext.tsx
│       │   ├── MirrorContext.tsx
│       │   ├── AppRegistry.ts
│       │   └── registerComponents.ts
│       └── types/
│           └── schema.ts           # TypeScript types
├── docs/                           # Documentation
│   ├── architecture/
│   │   └── mirror_modular_design_v2.md
│   └── guides/
│       └── implementation_guide.md
└── vite.config.ts                  # Vite configuration
```

---

## 🎯 What You Can Do Now

### 1. Switch to SAGE App

Edit `src/pages/Home.tsx` and change:
```typescript
app = await appRegistry.load('dexabooks');
```
to:
```typescript
app = await appRegistry.load('sage');
```

### 2. Create a New App

1. Create a new directory in `src/apps/your-app/`
2. Add these files:
   - `app.json` - App manifest
   - `header.json` - Header layout
   - `navigator.json` - Navigator layout
   - `main.json` - Main viewport layout

3. Follow the same structure as `dexabooks` or `sage`

### 3. Add Custom Components

1. Create your component in `src/components/`
2. Register it in `src/core/registerComponents.ts`:
   ```typescript
   import MyComponent from '@/components/MyComponent';
   componentRegistry.register('MyComponent', MyComponent);
   ```
3. Use it in your schemas:
   ```json
   {
     "type": "MyComponent",
     "props": {
       "title": "Hello World"
     }
   }
   ```

### 4. Connect to Core API

Update the `apiBaseUrl` in `src/App.tsx`:
```typescript
<MirrorProvider apiBaseUrl="http://your-core-api:8001">
```

Then use the API in your components:
```typescript
const { api } = useMirror();
const data = await api.get('/your-endpoint');
```

---

## 🛠️ Development Tips

### Hot Module Replacement (HMR)
Vite automatically reloads when you save files. Changes to:
- Components → Instant reload
- Schemas → Instant reload
- Config files → May require server restart

### Console Logging
Check the browser console for:
- Component registration messages
- App discovery logs
- Schema loading status
- Event bus activity

### TypeScript Checking
```bash
npm run check
# or
pnpm check
```

---

## 📚 Learn More

- **Architecture:** `/docs/architecture/mirror_modular_design_v2.md`
- **Implementation Guide:** `/docs/guides/implementation_guide.md`
- **Deployment:** `/mirror/DEPLOYMENT_GUIDE.md`

---

## 🐛 Troubleshooting

### "Component not found" error
→ Make sure the component is registered in `registerComponents.ts`

### "Schema not found" error
→ Check that the JSON file exists in `/src/apps/`

### Blank page
→ Check browser console for errors
→ Verify dev server is running on port 5173

### Port already in use
→ Kill the process: `pkill -9 -f vite`
→ Or use a different port in `vite.config.ts`

---

**Happy Building! 🎉**
