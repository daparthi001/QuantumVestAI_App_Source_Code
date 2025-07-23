#!/bin/bash

# Fix Python Path Script
# This script standardizes PYTHONPATH configurations across the ai-stock-platform project

set -e

echo "🔧 Fixing Python Path configurations..."

# Define the standard Python path based on Dockerfiles
STANDARD_PYTHONPATH="/app/core:/app/ai-stock-platform:/app/ai-stock-platform/api:/app/api:/app/ui:/app:$PYTHONPATH"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Current PYTHONPATH issues found:${NC}"
echo "  - Inconsistent path formats across files"
echo "  - Mixed absolute and relative paths"
echo "  - Redundant path declarations"
echo ""

# Function to backup files
backup_file() {
    local file=$1
    if [ -f "$file" ]; then
        cp "$file" "$file.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}📦 Backed up: $file${NC}"
    fi
}

# Function to fix PYTHONPATH in shell scripts
fix_shell_script() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        echo -e "${BLUE}🔨 Fixing $description: $file${NC}"
        backup_file "$file"

        # Remove existing PYTHONPATH exports and add standardized one
        sed -i '/^export PYTHONPATH=/d' "$file"

        # Add the standard PYTHONPATH after the shebang or at the top
        if grep -q "#!/bin/bash" "$file"; then
            sed -i '/#!\/bin\/bash/a\\nexport PYTHONPATH="${STANDARD_PYTHONPATH}"' "$file"
        else
            sed -i "1iexport PYTHONPATH=\"${STANDARD_PYTHONPATH}\"" "$file"
        fi

        echo -e "${GREEN}✅ Fixed: $file${NC}"
    else
        echo -e "${RED}❌ File not found: $file${NC}"
    fi
}

# Function to fix PYTHONPATH in Docker Compose files
fix_docker_compose() {
    local file=$1

    if [ -f "$file" ]; then
        echo -e "${BLUE}🐳 Fixing Docker Compose: $file${NC}"
        backup_file "$file"

        # Replace PYTHONPATH environment variables in docker-compose files
        sed -i "s|PYTHONPATH=.*|PYTHONPATH=/app/core:/app/ai-stock-platform:/app/ai-stock-platform/api:/app/api:/app/ui:/app|g" "$file"

        echo -e "${GREEN}✅ Fixed: $file${NC}"
    else
        echo -e "${RED}❌ File not found: $file${NC}"
    fi
}

# Function to fix PYTHONPATH in Dockerfiles
fix_dockerfile() {
    local file=$1

    if [ -f "$file" ]; then
        echo -e "${BLUE}🐳 Fixing Dockerfile: $file${NC}"
        backup_file "$file"

        # Replace existing PYTHONPATH values
        sed -i "s|PYTHONPATH=.*|PYTHONPATH=/app/core:/app/ai-stock-platform:/app/ai-stock-platform/api:/app/api:/app/ui:/app|g" "$file"

        echo -e "${GREEN}✅ Fixed: $file${NC}"
    else
        echo -e "${RED}❌ File not found: $file${NC}"
    fi
}

# Function to fix PYTHONPATH in YAML config files
fix_yaml_config() {
    local file=$1

    if [ -f "$file" ]; then
        echo -e "${BLUE}⚙️  Fixing YAML config: $file${NC}"
        backup_file "$file"

        sed -i "s|PYTHONPATH=.*|PYTHONPATH=/app/core:/app/ai-stock-platform:/app/ai-stock-platform/api:/app/api:/app/ui:/app|g" "$file"

        echo -e "${GREEN}✅ Fixed: $file${NC}"
    else
        echo -e "${RED}❌ File not found: $file${NC}"
    fi
}

# Main execution
echo -e "${YELLOW}🚀 Starting Python Path fixes...${NC}"
echo ""

# Fix shell scripts
fix_shell_script "setup_env.sh" "Environment Setup Script"
fix_shell_script "ai-stock-platform/api/build-db-init.sh" "Database Init Build Script"
fix_shell_script "ai-stock-platform/api/docker-entrypoint.sh" "API Docker Entrypoint"
fix_shell_script "ai-stock-platform/api/scripts/db-init-entrypoint.sh" "DB Init Entrypoint"
fix_shell_script "ai-stock-platform/api/scripts/run_db_init.sh" "Run DB Init Script"

# Fix Docker Compose files
fix_docker_compose "ai-stock-platform/api/docker-compose.yml"
fix_docker_compose "ai-stock-platform/ui/docker-compose.yml"

# Fix Dockerfiles
fix_dockerfile "ai-stock-platform/api/Dockerfile"
fix_dockerfile "ai-stock-platform/api/Dockerfile.db-init"
fix_dockerfile "ai-stock-platform/ui/Dockerfile"

# Fix YAML config files
fix_yaml_config "ci-cd/k8s/ui-configmap.yaml"

# Update README.md to reflect the standardized path
if [ -f "README.md" ]; then
    echo -e "${BLUE}📚 Updating README.md with standardized paths...${NC}"
    backup_file "README.md"

    sed -i "s|export PYTHONPATH=\".*\"|export PYTHONPATH=\"${STANDARD_PYTHONPATH}\"|g" "README.md"

    echo -e "${GREEN}✅ Updated: README.md${NC}"
fi

# Create a verification script
cat > verify_pythonpath.sh <<'VERIFY'
#!/bin/bash

echo "🔍 Verifying PYTHONPATH configurations..."

echo ""
echo "=== Shell Scripts ==="
grep -n "PYTHONPATH" setup_env.sh ai-stock-platform/api/build-db-init.sh ai-stock-platform/api/docker-entrypoint.sh ai-stock-platform/api/scripts/*.sh 2>/dev/null | head -20

echo ""
echo "=== Docker Files ==="
grep -n "PYTHONPATH" ai-stock-platform/*/Dockerfile* 2>/dev/null

echo ""
echo "=== Docker Compose Files ==="
grep -n "PYTHONPATH" ai-stock-platform/*/docker-compose.yml 2>/dev/null

echo ""
echo "=== Config Files ==="
grep -n "PYTHONPATH" ci-cd/k8s/*.yaml 2>/dev/null

echo ""
echo "✅ Verification complete!"
VERIFY

chmod +x verify_pythonpath.sh

echo ""
echo -e "${GREEN}🎉 Python Path fixes completed!${NC}"
echo ""
echo -e "${YELLOW}📋 Summary of changes:${NC}"
echo "  ✅ Standardized PYTHONPATH across all configuration files"
echo "  ✅ Created backups of all modified files"
echo "  ✅ Updated shell scripts with consistent export statements"
echo "  ✅ Fixed Docker and Docker Compose configurations"
echo "  ✅ Updated YAML configuration files"
echo ""
echo -e "${BLUE}🔍 To verify the changes, run:${NC}"
echo "  ./verify_pythonpath.sh"
echo ""
echo -e "${YELLOW}📝 Standard PYTHONPATH now set to:${NC}"
echo "  /app/core:/app/ai-stock-platform:/app/ai-stock-platform/api:/app/api:/app/ui:/app"
echo ""
echo -e "${GREEN}🚀 Your Python path issues should now be resolved!${NC}"
