# test_freelancer.py (project root, throwaway — don't commit)
from agents.freelancer_agent import compute_price_floor

result = compute_price_floor(
    project_id="0387c16a-d3fe-4385-9a9d-cef12b9877b9",
    version_id="e21d02a7-8ebb-4858-af47-c8d79b89f3b4",
    freelancer_profile_id="72531437-5384-4aee-8734-38898c2f9547",
    rate_expectation=50.0,
)
print(result)