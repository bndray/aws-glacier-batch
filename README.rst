# Script for batch processing glacier vaults and contained archives (eg for deleting each archive in turn)

# Quick start
1. Add your account and region in aws-glacier.py (lines 6-7)
2. Define `json_parsed` array with your vaults
3. `poetry run initiate` 
4. `poetry run status` 
5. `poetry run download`
6. `poetry run delete`  

