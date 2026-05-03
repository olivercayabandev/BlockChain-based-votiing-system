import requests

base = 'https://block-chain-based-votiing-system.vercel.app'

print('Checking Vercel deployment...')
r = requests.get(base, timeout=10)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    print('Frontend is live!')
    print()
    print('HOW TO FIX MOBILE CHROME ISSUE:')
    print('=' * 50)
    print('1. Open Chrome on your phone')
    print('2. Go to: https://block-chain-based-votiing-system.vercel.app')
    print('3. Tap the 3-dot menu (top right)')
    print('4. Select "Clear browsing data"')
    print('5. Check "Cached images and files"')
    print('6. Tap "Clear data"')
    print('7. Reload the page')
    print()
    print('OR try these alternatives:')
    print('- Force refresh: Pull down hard on the page')
    print('- Open in Incognito mode: 3-dot menu -> New Incognito tab')
    print('- Uninstall and reinstall Chrome app')
    print()
    print('If issue persists, try:')
    print('- Different browser (Safari, Firefox, Edge)')
    print('- Different network (switch WiFi/4G)')
