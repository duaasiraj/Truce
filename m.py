from fireworks import Fireworks

client = Fireworks()

response = client.chat.completions.create(
  model="accounts/fireworks/models/gpt-oss-20b",
  messages=[{
    "role": "user",
    "content": "Say hello in Spanish",
  }],
)

print(response.choices[0].message.content)