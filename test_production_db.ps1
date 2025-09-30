# Production Analytics Database Test Script
# PowerShell script to test if production analytics database is working

Write-Host "=" * 60
Write-Host "PRODUCTION ANALYTICS DATABASE TEST"
Write-Host "=" * 60

# Test 1: Send analytics data
Write-Host "`n1️⃣ Sending test analytics data to production..."

$testData = @{
    guide_id = "test-schema-check-$(Get-Date -Format 'MMddHHmmss')"
    guide_title = "Test Schema Check"
    href = "/guides/test-schema-check"
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
    "User-Agent" = "PowerShell-Schema-Test/1.0"
}

try {
    $response = Invoke-WebRequest -Uri "https://www.proptradetools.com/analytics/guide-click" -Method POST -Body $testData -Headers $headers
    
    if ($response.StatusCode -eq 200) {
        $result = $response.Content | ConvertFrom-Json
        if ($result.ok) {
            Write-Host "✅ Analytics endpoint accepted the data"
            $testGuideId = ($testData | ConvertFrom-Json).guide_id
            Write-Host "   Test guide ID: $testGuideId"
        } else {
            Write-Host "❌ Analytics endpoint returned error: $($result | ConvertTo-Json)"
            exit 1
        }
    } else {
        Write-Host "❌ Analytics endpoint returned status $($response.StatusCode)"
        exit 1
    }
} catch {
    Write-Host "❌ Failed to send analytics data: $($_.Exception.Message)"
    exit 1
}

# Test 2: Wait and check if data was stored
Write-Host "`n2️⃣ Waiting 5 seconds for data to be processed..."
Start-Sleep -Seconds 5

Write-Host "`n3️⃣ Checking if test data was stored in database..."

try {
    $response = Invoke-WebRequest -Uri "https://www.proptradetools.com/analytics/popular?days=1&limit=50" -Method GET
    
    if ($response.StatusCode -eq 200) {
        $data = $response.Content | ConvertFrom-Json
        $guides = $data.guides
        
        # Look for our test data
        $testFound = $guides | Where-Object { $_.id -eq $testGuideId }
        
        if ($testFound) {
            Write-Host "✅ SUCCESS! Test data found in database!"
            Write-Host "   Production analytics database is working correctly"
            Write-Host "   Found $($guides.Count) total guides with analytics data"
            
            if ($guides.Count -gt 0) {
                Write-Host "`n   Recent analytics data:"
                $guides | Select-Object -First 10 | ForEach-Object {
                    Write-Host "     - $($_.id): $($_.clicks) clicks"
                }
            }
        } else {
            Write-Host "❌ PROBLEM: Test data not found in analytics results"
            Write-Host "   This means data is not being stored in the database"
            Write-Host "   Analytics endpoint accepts data but doesn't persist it"
            
            if ($guides.Count -gt 0) {
                Write-Host "`n   Existing analytics data found:"
                $guides | Select-Object -First 5 | ForEach-Object {
                    Write-Host "     - $($_.id): $($_.clicks) clicks"
                }
                Write-Host "   (This suggests the database connection works, but our test data wasn't stored)"
            } else {
                Write-Host "   No analytics data found at all - database may be empty or disconnected"
            }
        }
    } else {
        Write-Host "❌ Popular guides API returned status $($response.StatusCode)"
        exit 1
    }
} catch {
    Write-Host "❌ Failed to retrieve analytics data: $($_.Exception.Message)"
    exit 1
}

Write-Host "`n" + "=" * 60
Write-Host "DIAGNOSTIC SUMMARY"
Write-Host "=" * 60

if ($testFound) {
    Write-Host "✅ RESULT: Production analytics database is working correctly!"
    Write-Host "`n🔥 This means flame icons should appear on guides with enough clicks."
    Write-Host "   Current flame threshold: 5 clicks (from FLAME_ICON_THRESHOLD)"
    Write-Host "   Guides need 5+ clicks in 30 days to show the flame icon."
} else {
    Write-Host "❌ RESULT: Production analytics database has storage issues!"
    Write-Host "`n🔧 POSSIBLE CAUSES:"
    Write-Host "   1. DATABASE_URL not configured correctly"
    Write-Host "   2. Analytics tables don't exist in production database"
    Write-Host "   3. Database permissions issues"
    Write-Host "   4. Transaction not being committed"
    
    Write-Host "`n💡 NEXT STEPS:"
    Write-Host "   1. Check Heroku config: heroku config | findstr DATABASE_URL"
    Write-Host "   2. Check database tables: heroku pg:psql -c '\dt'"
    Write-Host "   3. Create tables if missing (see check_database_schema.py)"
    Write-Host "   4. Check production logs: heroku logs --tail"
}

Write-Host "`n🔍 To check current production analytics data:"
Write-Host "   Visit: https://www.proptradetools.com/analytics/popular?days=30&limit=10"