# Similar changes for all other router files
# Remove the prefix in the APIRouter initialization
router = APIRouter(
    # prefix="/users",  # Remove this duplicate prefix
    tags=["users"]
)

# Update route paths to include the module name
@router.get("/users/me", ...)
# ...