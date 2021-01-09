from pyzoom import ZoomClient

client = ZoomClient('G7Ok6MTgT9OeacitMPeKjA', 'vBV1hEHyqBlp5DfGMJEt47pVu1W9HEMf5gji')

# Get self
response = client.raw.get('/me')

# Get all pages of meeting participants
result_dict = client.raw.get_all_pages('/past_meetings/{meetingUUID}/participants')
print(result_dict)