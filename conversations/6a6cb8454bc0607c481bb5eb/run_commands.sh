
pages=("referral" "incentives" "api" "api/docs" "contact")

for PAGE in "${pages[@]}"; do
    echo "=================================================="
    echo "PAGE: $PAGE"
    echo "=================================================="
    echo "--- HTTP CODE ---"
    curl -sk -o /dev/null -w '%{http_code}' "https://verdischain.com/$PAGE/"
    echo ""
    
    echo "--- UNSTYLED HEADINGS ---"
    grep -oP '<h[1-6][^>]*>' "/var/www/verdiscan/$PAGE/index.html" 2>/dev/null | grep -v 'class=' | head -10
    
    echo "--- INTERNAL LINKS ---"
    grep -oP 'href="/[^"]*"' "/var/www/verdiscan/$PAGE/index.html" 2>/dev/null | sed 's/href="//;s/"//' | sort -u | while read url; do
        status=$(curl -sk -o /dev/null -w '%{http_code}' "https://verdischain.com${url}" 2>/dev/null)
        echo "$url -> $status"
    done
    
    echo "--- HUGE TEXT ---"
    grep -oP 'font-size:\s*([3-9][0-9]|[1-9][0-9]{2})px' "/var/www/verdiscan/$PAGE/index.html" 2>/dev/null | sort -u
    
    echo "--- LOGO ---"
    grep -oP 'src="[^"]*logo[^"]*"' "/var/www/verdiscan/$PAGE/index.html" 2>/dev/null | head -3
    
    echo "--- NAV LINKS ---"
    grep -oP '<a[^>]*href="/[^"]*"[^>]*>[^<]*</a>' "/var/www/verdiscan/$PAGE/index.html" 2>/dev/null | head -15
    echo ""
done

echo "=================================================="
echo "EXISTENCE CHECK FOR /api/ AND /contact/"
echo "=================================================="
echo "/api/ status: $(curl -sk -o /dev/null -w '%{http_code}' https://verdischain.com/api/)"
echo "/contact/ status: $(curl -sk -o /dev/null -w '%{http_code}' https://verdischain.com/contact/)"
echo "/api/docs/ status: $(curl -sk -o /dev/null -w '%{http_code}' https://verdischain.com/api/docs/)"
