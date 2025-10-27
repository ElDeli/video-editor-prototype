#!/bin/bash

echo "=========================================================================="
echo "🏥 VIDEO EDITOR PROTOTYPE - COMPLETE SYSTEM HEALTH CHECK"
echo "=========================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
WARNINGS=0
ERRORS=0

# ============================================================================
# 1. CHECK LOCAL BACKEND (Port 5001)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 1. LOCAL BACKEND CHECK (localhost:5001)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if lsof -ti:5001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running on port 5001${NC}"
    ((PASSED++))
    
    # Test health endpoint
    HEALTH=$(curl -s http://localhost:5001/api/health 2>&1)
    if [[ $HEALTH == *"status"* ]]; then
        echo -e "${GREEN}✅ Health endpoint responding${NC}"
        echo "   Response: $HEALTH"
        ((PASSED++))
    else
        echo -e "${RED}❌ Health endpoint not responding${NC}"
        ((ERRORS++))
    fi
    
    # Test projects endpoint
    PROJECTS=$(curl -s http://localhost:5001/api/projects 2>&1)
    if [[ $PROJECTS == *"["* ]] || [[ $PROJECTS == *"projects"* ]]; then
        echo -e "${GREEN}✅ Projects endpoint responding${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  Projects endpoint: $PROJECTS${NC}"
        ((WARNINGS++))
    fi
    
else
    echo -e "${RED}❌ Backend NOT running on port 5001${NC}"
    echo "   Run: ./start_all.command"
    ((ERRORS++))
fi

echo ""

# ============================================================================
# 2. CHECK LOCAL FRONTEND (Port 3000)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 2. LOCAL FRONTEND CHECK (localhost:3000)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if lsof -ti:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is running on port 3000${NC}"
    ((PASSED++))
    
    # Test if frontend is accessible
    FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>&1)
    if [[ $FRONTEND == "200" ]]; then
        echo -e "${GREEN}✅ Frontend accessible (HTTP 200)${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  Frontend returned: HTTP $FRONTEND${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}❌ Frontend NOT running on port 3000${NC}"
    echo "   Run: ./start_all.command"
    ((ERRORS++))
fi

echo ""

# ============================================================================
# 3. CHECK RAILWAY DEPLOYMENT
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚂 3. RAILWAY DEPLOYMENT CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RAILWAY_STATUS=$(railway status 2>&1)
if [[ $RAILWAY_STATUS == *"Video-Editor-Prototype"* ]]; then
    echo -e "${GREEN}✅ Railway linked: Video-Editor-Prototype${NC}"
    ((PASSED++))
    
    # Get Railway URL
    RAILWAY_DOMAIN=$(railway domain 2>&1 | grep -o 'https://[^[:space:]]*' | head -1)
    if [[ -n $RAILWAY_DOMAIN ]]; then
        echo -e "${GREEN}✅ Railway URL: $RAILWAY_DOMAIN${NC}"
        ((PASSED++))
        
        # Test Railway health endpoint
        echo "   Testing Railway deployment..."
        RAILWAY_HEALTH=$(curl -s -m 10 "$RAILWAY_DOMAIN/api/health" 2>&1)
        if [[ $RAILWAY_HEALTH == *"status"* ]]; then
            echo -e "${GREEN}✅ Railway backend responding${NC}"
            echo "   Response: $RAILWAY_HEALTH"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠️  Railway backend: $RAILWAY_HEALTH${NC}"
            ((WARNINGS++))
        fi
    else
        echo -e "${YELLOW}⚠️  Could not get Railway domain${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}❌ Railway NOT linked${NC}"
    echo "   Run: railway link"
    ((ERRORS++))
fi

echo ""

# ============================================================================
# 4. CHECK GIT REPOSITORY
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 4. GIT REPOSITORY CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d ".git" ]; then
    echo -e "${GREEN}✅ Git repository initialized${NC}"
    ((PASSED++))
    
    GIT_REMOTE=$(git remote get-url origin 2>&1)
    if [[ $GIT_REMOTE == *"github.com"* ]]; then
        echo -e "${GREEN}✅ Git remote: ${GIT_REMOTE}${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ Git remote not configured${NC}"
        ((ERRORS++))
    fi
    
    GIT_BRANCH=$(git branch --show-current 2>&1)
    echo -e "${GREEN}✅ Current branch: $GIT_BRANCH${NC}"
    ((PASSED++))
    
    # Check for uncommitted changes
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        echo -e "${GREEN}✅ Working directory clean${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  Uncommitted changes present${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}❌ Git repository NOT initialized${NC}"
    ((ERRORS++))
fi

echo ""

# ============================================================================
# 5. CHECK DROPBOX STORAGE
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 5. DROPBOX STORAGE CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

OUTPUT_PATH="$HOME/Library/CloudStorage/Dropbox/Apps/output Horoskop/output/video_editor_prototype"
if [ -d "$OUTPUT_PATH" ]; then
    echo -e "${GREEN}✅ Dropbox output folder exists${NC}"
    echo "   Path: $OUTPUT_PATH"
    ((PASSED++))
    
    # Check image_cache
    if [ -d "$OUTPUT_PATH/image_cache" ]; then
        IMAGE_COUNT=$(find "$OUTPUT_PATH/image_cache" -type f | wc -l | xargs)
        echo -e "${GREEN}✅ image_cache: $IMAGE_COUNT files${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  image_cache folder not found${NC}"
        ((WARNINGS++))
    fi
    
    # Check uploads
    if [ -d "$OUTPUT_PATH/uploads" ]; then
        echo -e "${GREEN}✅ uploads folder exists${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  uploads folder not found${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}❌ Dropbox output folder NOT found${NC}"
    ((ERRORS++))
fi

echo ""

# ============================================================================
# 6. CHECK MAC SYNC POLLER
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 6. MAC SYNC POLLER CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "mac_sync_poller.py" ]; then
    echo -e "${GREEN}✅ mac_sync_poller.py exists${NC}"
    ((PASSED++))
    
    # Check if running
    if pgrep -f "mac_sync_poller.py" > /dev/null; then
        echo -e "${GREEN}✅ Mac Sync Poller is running${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  Mac Sync Poller NOT running${NC}"
        echo "   Start with: ./start_all.command"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}❌ mac_sync_poller.py NOT found${NC}"
    ((ERRORS++))
fi

echo ""

# ============================================================================
# 7. CHECK DIRECTORY STRUCTURE
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 7. DIRECTORY STRUCTURE CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

REQUIRED_DIRS=("backend" "frontend" "logs" "backend/api" "backend/services" "backend/database")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅ $dir${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ MISSING: $dir${NC}"
        ((ERRORS++))
    fi
done

echo ""

# ============================================================================
# 8. CHECK CRITICAL FILES
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 8. CRITICAL FILES CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

CRITICAL_FILES=(
    "backend/app.py"
    "backend/services/dropbox_storage.py"
    "mac_sync_poller.py"
    "start_all.command"
    "stop_all.command"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ MISSING: $file${NC}"
        ((ERRORS++))
    fi
done

echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "=========================================================================="
echo "📊 HEALTH CHECK SUMMARY"
echo "=========================================================================="
echo ""

TOTAL=$((PASSED + WARNINGS + ERRORS))
PASSED_PCT=$((PASSED * 100 / TOTAL))

echo -e "${GREEN}✅ PASSED:   $PASSED / $TOTAL ($PASSED_PCT%)${NC}"
echo -e "${YELLOW}⚠️  WARNINGS: $WARNINGS${NC}"
echo -e "${RED}❌ ERRORS:   $ERRORS${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 SYSTEM STATUS: HEALTHY ✅${NC}"
    EXIT_CODE=0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  SYSTEM STATUS: MOSTLY HEALTHY (with warnings)${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}🔴 SYSTEM STATUS: ISSUES DETECTED${NC}"
    EXIT_CODE=1
fi

echo "=========================================================================="

exit $EXIT_CODE
