#!/usr/bin/env python3
"""
n64_games_js Games Grid Generator
Creates an Xemu-style grid website from your n64_games_js games JSON
Shows title as text overlay when image fails to load
Uses cartridge code for image filenames
"""

import json
import os

# Configuration
JSON_FILE = "n64_games_js.json"
OUTPUT_HTML = "n64_games_dolphin.html"
PLACEHOLDER_IMAGE = "https://raw.githubusercontent.com/igiteam/n64-covers/refs/heads/master/n64-cover-default.png"
RAW_BASE_URL = "https://raw.githubusercontent.com/igiteam/n64-covers/refs/heads/main/covers"

def load_games_data():
    """Load games from JSON file by matching cover files with cartridge codes"""
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found!")
        return None
    
    LABELS_FOLDER = "covers"
    if not os.path.exists(LABELS_FOLDER):
        print(f"Error: '{LABELS_FOLDER}' folder not found!")
        return None
    
    # STEP 1: Get all cover files first
    cover_files = []
    for f in os.listdir(LABELS_FOLDER):
        if f.endswith('.png'):
            # Store both the filename and the code without extension
            code_without_ext = f.replace('.png', '')
            cover_files.append({
                'filename': f,
                'code_upper': code_without_ext.upper(),
                'code_lower': code_without_ext.lower(),
                'code_original': code_without_ext
            })
    
    print(f"Found {len(cover_files)} cover images in {LABELS_FOLDER}/")
    print("Sample cover codes:", [c['code_original'] for c in cover_files[:5]])
    
    # STEP 2: Load JSON data
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        games = json.load(f)
    
    # STEP 3: Create a lookup dictionary for faster matching
    # Key: cartridge code variations, Value: cover file info
    cover_lookup = {}
    for cover in cover_files:
        # Store multiple variations of the code for matching
        cover_lookup[cover['code_upper']] = cover
        cover_lookup[cover['code_lower']] = cover
        cover_lookup[cover['code_original']] = cover
        
        # Also store without region (last part after last dash)
        if '-' in cover['code_original']:
            parts = cover['code_original'].split('-')
            if len(parts) > 1:
                # Try without the last part
                without_last = '-'.join(parts[:-1])
                cover_lookup[without_last.upper()] = cover
                cover_lookup[without_last.lower()] = cover
    
    # STEP 4: Match games with covers
    matched_games = []
    seen_titles = set()
    matched_count = 0
    no_code_count = 0
    no_match_count = 0
    
    # For debugging - track which covers were used
    used_covers = set()
    
    # Loop through each cover file and find matching game
    for cover in cover_files:
        cover_code = cover['code_original']
        found_match = False
        
        # Search through games for a matching cartridge_code
        for game in games:
            # Skip if no good_name
            if 'good_name' not in game or not game['good_name']:
                continue
            
            # Check for cartridge_code in various possible fields
            game_code = None
            if 'cartridge_code' in game and game['cartridge_code']:
                game_code = game['cartridge_code']
            elif 'rom_id' in game and game['rom_id']:
                # Try rom_id as fallback
                game_code = game['rom_id']
            
            if not game_code:
                continue
            
            # Clean up game code
            game_code_clean = str(game_code).strip()
            game_code_upper = game_code_clean.upper()
            game_code_lower = game_code_clean.lower()
            
            # Check if this game matches the cover
            if (game_code_upper == cover['code_upper'] or 
                game_code_lower == cover['code_lower'] or
                game_code_clean == cover['code_original']):
                
                title = game['good_name']
                
                # Avoid duplicates by title
                if title not in seen_titles:
                    seen_titles.add(title)
                    
                    # Add cover info to game data
                    game['cover_filename'] = cover['filename']
                    game['matched_code'] = game_code_clean
                    
                    matched_games.append(game)
                    matched_count += 1
                    used_covers.add(cover['filename'])
                    found_match = True
                    print(f"✓ Matched: {cover['filename']} -> {title}")
                    break
        
        if not found_match:
            no_match_count += 1
            if no_match_count <= 10:  # Show first 10 unmached covers
                print(f"✗ No match for cover: {cover['filename']}")
    
    # Also check for games with codes that might not have covers
    games_without_covers = 0
    for game in games:
        if 'cartridge_code' in game and game['cartridge_code']:
            code = game['cartridge_code'].upper()
            expected_file = f"{code}.png"
            if expected_file not in used_covers and expected_file.lower() not in [c.lower() for c in used_covers]:
                games_without_covers += 1
    
    print(f"\n📊 Cover Matching Results:")
    print(f"   - Total cover files: {len(cover_files)}")
    print(f"   - Games matched with covers: {matched_count}")
    print(f"   - Covers with no game match: {no_match_count}")
    print(f"   - Games in JSON with codes but no cover: {games_without_covers}")
    
    if matched_count == 0:
        print("\n❌ No matches found!")
        print("   Please check your naming convention.")
        print("   Example cover: 'NUS-NFUE-USA.png'")
        print("   Should match game with cartridge_code: 'NUS-NFUE-USA'")
    
    return matched_games

def get_cartridge_image_url(game):
    """Generate image URL from cartridge code if available"""
    if 'cartridge_code' in game and game['cartridge_code']:
        cartridge_code = game['cartridge_code'].strip()
        image_filename = f"{cartridge_code.upper()}.png"
        return f"{RAW_BASE_URL}/{image_filename}"
    
    return PLACEHOLDER_IMAGE

def generate_html(games):
    """Generate the grid website HTML"""
    
    games.sort(key=lambda x: x['good_name'].lower())
    
    total_games = len(games)
    with_covers = 0
    
    html = f"""<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>N64 Games Collection</title>

  <link rel="icon" href="https://cdn.sdappnet.cloud/rtx/images/n64-icon.png" type="image/png">
  <link rel="apple-touch-icon" href="https://cdn.sdappnet.cloud/rtx/images/n64-icon.png" sizes="180x180">
  <link rel="icon" type="image/png" href="https://cdn.sdappnet.cloud/rtx/images/n64-icon.png" sizes="192x192">
  <link rel="icon" type="image/png" href="https://cdn.sdappnet.cloud/rtx/images/n64-icon.png" sizes="512x512">
  <meta itemprop="name" content="N64 Games Collection">
  <meta property="og:title" content="N64 Games Collection">
  <meta property="og:url" content="">
  <meta property="og:type" content="website">
  <meta name="twitter:title" content="N64 Games Collection">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="apple-touch-icon" href="https://cdn.sdappnet.cloud/rtx/images/n64-icon.png" sizes="180x180">

  <style>
    body {{
      background-color: #1a1a1a;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      margin: 4px 20px;
      padding: 0;
    }}

    #results {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 10px;
      max-width: 1400px;
      margin: 0 auto;
      background-color: #1a1a1a;
      margin-top: 4px;
      z-index: 1000;
    }}

    .title-card {{
      background: #2a2a2a;
      border-radius: 8px;
      overflow: hidden;
      transition: transform 0.2s;
    }}

    .title-card:hover {{
      transform: scale(1.05);
      z-index: 10;
    }}

    .title-card-container {{
      width: 100%;
      position: relative;
    }}

    .title-card-image-container {{
      width: 100%;
      aspect-ratio: 4/3;
      overflow: hidden;
      position: relative;
      background-color: #1a1a1a;
    }}

    .title-card-image-container img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: opacity 0.3s;
    }}

    .title-card-image-container .fallback-title {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 10px;
      box-sizing: border-box;
      background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
      color: #888;
      font-size: 14px;
      font-weight: 500;
      word-break: break-word;
      border: 1px solid #333;
    }}

    .fill-color-Playable {{
      background-color: #42991b !important;
      color: white !important;
      font-weight: 700 !important;
    }}

    .card-body {{
      flex: 1 1 auto;
      min-height: 1px;
      padding: 0.5rem 1.25rem !important;
    }}

    .text-center {{
      text-align: center !important;
    }}

    .py-1 {{
      padding-top: 0.25rem !important;
      padding-bottom: 0.25rem !important;
    }}

    .my-0 {{
      margin-top: 0 !important;
      margin-bottom: 0 !important;
    }}

    small {{
      font-size: 80%;
    }}

    a {{
      text-decoration: none;
      color: inherit;
    }}

    /* Search container */
    #saved-search-container {{
      position: sticky;
      z-index: 10000;
      margin-left: auto;
      margin-right: auto;
      margin: 8px 0px;
    }}

    #saved-search-input {{
      padding: 10px;
      width: calc(100% - 20px);
      border: 1px solid #555;
      border-radius: 4px;
      background: #444;
      color: white;
      flex: 1;
    }}

    .search-row {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .icon {{
      width: 34px;
      height: 34px;
      border-radius: 4px;
      object-fit: cover;
    }}

    #saved-search-input::placeholder {{
      color: #aaa;
    }}

    #saved-results-count {{
      color: white;
      font-size: 14px;
      text-align: center;
      margin-top: 5px;
    }}

    /* Hide cards with failed images */
    .title-card.image-failed {{
      display: none !important;
    }}

    /* Hide cards when searching */
    .title-card-link.hidden-game {{
      display: none !important;
    }}
  </style>
</head>

<body>
  <div id="saved-search-container">
    <div class="search-row">
      <img src="https://cdn.sdappnet.cloud/rtx/images/n64-icon.png" class="icon" alt="N64 logo">
      <input type="text" id="saved-search-input" placeholder="Search games...">
      <a href="https://www.aliexpress.com/item/1005007539923790.html" target="_blank">
        <img src="https://cdn.sdappnet.cloud/rtx/images/n64-controller.png" class="icon" alt="N64 Controller">
      </a>
      <a href="https://cdn.sdappnet.cloud/rtx/n64_magazine.html" target="_blank">
        <img src="https://cdn.sdappnet.cloud/rtx/images/n64-magazine.png" class="icon" alt="N64 Magazine">
      </a>
    </div>
    <div id="saved-results-count"></div>
  </div>

  <div class="row" id="results">
"""

    for game in games:
        title = game['good_name'].replace('"', '&quot;')
        
        cover_url = get_cartridge_image_url(game)
        has_cartridge_code = 'cartridge_code' in game and game['cartridge_code']
        
        if has_cartridge_code:
            with_covers += 1
        
        cartridge_code = game.get('cartridge_code', '')
        
        html += f"""
    <div class="col px-1 mb-4 title-card" data-title-name="{title}" data-cartridge="{cartridge_code}">
      <a target="_blank" rel="norefferer" href="https://github.com/igiteam/n64-covers">
        <div class="mx-auto title-card-container">
          <div class="title-card-image-container" style="position: relative;">
            <img
              src="{cover_url}"
              loading="lazy"
              title="{title}"
              data-cartridge="{cartridge_code}"
              onload="this.nextElementSibling.style.display='none';"
              onerror="this.closest('.title-card').classList.add('image-failed');">
            <div class="fallback-title" style="display: flex; position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(transparent, rgba(0,0,0,0.9)); color: white; padding: 15px 8px 8px 8px; font-size: 12px; text-align: center; font-weight: 500;">{title}</div>
          </div>
          <div class="fill-color-Playable card-body text-center py-1 my-0"><small><strong>Play</strong></small></div>
        </div>
      </a>
    </div>"""

    html += f"""
  </div>

  <script>
    // Convert title cards to links for search functionality
    function wrapCardsWithLinks() {{
      document.querySelectorAll('.title-card').forEach(card => {{
        // Skip if card image failed
        if (card.classList.contains('image-failed')) return;

        const title = card.getAttribute('data-title-name');
        
        const existingInnerLink = card.querySelector('a');
        if (existingInnerLink) {{
          while (existingInnerLink.firstChild) {{
            card.insertBefore(existingInnerLink.firstChild, existingInnerLink);
          }}
          existingInnerLink.remove();
        }}

        let url_path = '';
        if (title) {{
          url_path = title
            .toLowerCase()
            .replace(/[^\\w\\s-]/g, '')
            .replace(/\\s+/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '');
        }}

        if (url_path) {{
          const link = document.createElement('a');
          link.href = 'https://meyt.netlify.app/search/' + url_path + ' n64';
          link.className = 'title-card-link';
          link.rel = 'noopener noreferrer';
          link.target = '_blank';
          
          if (title) link.setAttribute('data-title-name', title);

          card.parentNode.insertBefore(link, card);
          link.appendChild(card);
        }}
      }});
    }}

    // Run link wrapping after a delay
    setTimeout(wrapCardsWithLinks, 1000);

    // Search functionality
    document.getElementById('saved-search-input').addEventListener('input', function (e) {{
      const searchTerm = e.target.value.toLowerCase();
      const links = document.querySelectorAll('.title-card-link');
      let count = 0;

      links.forEach(link => {{
        const title = link.getAttribute('data-title-name') || '';

        if (title.toLowerCase().includes(searchTerm) && searchTerm) {{
          link.classList.remove('hidden-game');
          count++;
        }} else if (searchTerm) {{
          link.classList.add('hidden-game');
        }} else {{
          link.classList.remove('hidden-game');
        }}
      }});

      document.getElementById('saved-results-count').textContent =
        searchTerm ? `Found ${{count}} game${{count !== 1 ? 's' : ''}}` : '';
    }});

    // Keyboard shortcut
    document.addEventListener('keydown', function(e) {{
      if (e.key === '/' && !document.getElementById('saved-search-input').matches(':focus')) {{
        e.preventDefault();
        document.getElementById('saved-search-input').focus();
      }}
    }});

    // Initial hide of any images that already failed
    document.querySelectorAll('.title-card img').forEach(img => {{
      if (img.complete && img.naturalHeight === 0) {{
        img.closest('.title-card').classList.add('image-failed');
      }}
    }});
  </script>
</body>

</html>
"""

    return html, with_covers

def main():
    print("N64 Games Grid Generator")
    print("=" * 50)
    
    games = load_games_data()
    if not games:
        return
    
    print("Generating grid website with cartridge code images...")
    html_content, with_covers = generate_html(games)
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Website generated: {OUTPUT_HTML}")
    print(f"\nStatistics:")
    print(f"   - Total games: {len(games)}")
    print(f"   - Games with cartridge codes: {with_covers}")
    print(f"\nImage URL format: {RAW_BASE_URL}/[cartridge_code].png")

if __name__ == "__main__":
    main()