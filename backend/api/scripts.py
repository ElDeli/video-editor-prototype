from flask import Blueprint, request, jsonify
import os
import sys
import re

scripts_bp = Blueprint('scripts', __name__)

def remove_emojis(text):
    """Remove all emojis and special symbols from text"""
    # Emoji pattern - matches all emoji characters
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

@scripts_bp.route('/scripts/improve', methods=['POST'])
def improve_script():
    """Improve script with AI for better viral potential"""
    try:
        data = request.get_json()
        if not data or 'script' not in data:
            return jsonify({'error': 'Script is required'}), 400

        original_script = data['script'].strip()
        if not original_script:
            return jsonify({'error': 'Script cannot be empty'}), 400

        target_duration = data.get('target_duration')  # Optional: in seconds

        # Check if OpenAI API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠️ No OPENAI_API_KEY found, returning original script", file=sys.stderr, flush=True)
            return jsonify({
                'improved_script': original_script,
                'message': 'AI improvement not available (no API key)'
            })

        # Use OpenAI to improve the script
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            print(f"\n🤖 Improving script with AI ({len(original_script)} chars)...", file=sys.stderr, flush=True)
            if target_duration:
                print(f"🎯 Target duration: {target_duration} seconds", file=sys.stderr, flush=True)

            # Build duration instruction if target duration is specified
            duration_instruction = ""
            if target_duration:
                # Calculate approximate word count (assuming ~2.5 words per second for natural speech)
                target_words = int(target_duration * 2.5)
                duration_instruction = f"\n\nIMPORTANT DURATION CONSTRAINT:\n- Adjust the script to fit approximately {target_duration} seconds of speech\n- Target around {target_words} words (at ~2.5 words/second)\n- Maintain quality while fitting this duration\n- If original is too long, shorten it strategically\n- If original is too short, expand key points naturally"

            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cost-effective
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert viral content creator for TikTok/Reels.
Your task: Improve scripts for SHORT-FORM VIDEO content (30-60 seconds).

Key improvements:
1. Hook: Start with attention-grabbing opener
2. Flow: Make it conversational, not robotic
3. Emotion: Add emotional triggers (curiosity, inspiration, urgency)
4. Pacing: Short punchy sentences for TikTok/Reels
5. CTA: Strong call-to-action at end
6. Language: Use "you" to connect directly with viewer

CRITICAL RULES:
- Keep the SAME TOPIC and MESSAGE
- Return ONLY the improved script (no explanations)
- PRESERVE THE ORIGINAL LANGUAGE - Do NOT translate! If input is English, output must be English. If input is German, output must be German.
- NEVER EVER use emojis or special symbols (no 👉 ❌ ✅ 🎯 💡 ⚡ 🔥 etc.)
- Text-to-speech cannot read emojis - use ONLY plain text and punctuation{duration_instruction}
"""
                    },
                    {
                        "role": "user",
                        "content": f"Improve this script for viral potential:\n\n{original_script}"
                    }
                ],
                temperature=0.8,
                max_tokens=800
            )

            improved_script = response.choices[0].message.content.strip()

            # Remove any emojis that might have slipped through
            improved_script = remove_emojis(improved_script)

            print(f"✅ Script improved! ({len(improved_script)} chars)", file=sys.stderr, flush=True)
            print(f"   Original: {original_script[:100]}...", file=sys.stderr, flush=True)
            print(f"   Improved: {improved_script[:100]}...\n", file=sys.stderr, flush=True)

            return jsonify({
                'improved_script': improved_script,
                'original_script': original_script,
                'message': 'Script improved with AI'
            })

        except Exception as e:
            print(f"❌ OpenAI API error: {e}", file=sys.stderr, flush=True)
            return jsonify({
                'improved_script': original_script,
                'message': f'AI improvement failed: {str(e)}'
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
