import time
import uuid
import pytest

@pytest.mark.asyncio
async def test_get_activities_aaa(async_client):
	# Arrange
	ts = int(time.time())

	# Act
	resp = await async_client.get(f"/activities?ts={ts}")

	# Assert
	assert resp.status_code == 200, f"Expected 200 from /activities, got {resp.status_code}"
	data = resp.json()
	assert isinstance(data, dict), "Expected JSON object (mapping) from /activities"
	if not data:
		pytest.skip("No activities defined in the app")

	# Further shape assertions (for first activity)
	name, details = next(iter(data.items()))
	assert "description" in details and "schedule" in details and "max_participants" in details and "participants" in details

@pytest.mark.asyncio
async def test_signup_and_unregister_flow_aaa(async_client):
	# Arrange
	ts = int(time.time())
	resp = await async_client.get(f"/activities?ts={ts}")
	assert resp.status_code == 200
	activities = resp.json()
	if not activities:
		pytest.skip("No activities defined in the app")

	activity_name = next(iter(activities.keys()))
	email = f"test-{uuid.uuid4().hex}@example.com"

	# Act: signup
	resp_signup = await async_client.post(f"/activities/{activity_name}/signup?email={email}")

	# Assert signup
	assert resp_signup.status_code in (200, 201, 202), f"Unexpected signup status: {resp_signup.status_code}"

	# Act: verify participant added
	resp_after = await async_client.get(f"/activities?ts={int(time.time())}")
	participants = resp_after.json()[activity_name].get("participants", [])

	# Assert participant present
	assert email in participants, "Email should appear in participants after signup"

	# Act: unregister
	resp_delete = await async_client.delete(f"/activities/{activity_name}/signup?email={email}")

	# Assert unregister
	assert resp_delete.status_code in (200, 202, 204), f"Unexpected delete status: {resp_delete.status_code}"

	# Act: final verify
	resp_final = await async_client.get(f"/activities?ts={int(time.time())}")
	final_participants = resp_final.json()[activity_name].get("participants", [])

	# Assert removal
	assert email not in final_participants, "Email should be removed after unregistering"
