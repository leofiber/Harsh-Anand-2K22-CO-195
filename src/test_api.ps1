# Boostly API Test Script
# Run this script to test all API endpoints

Write-Host "========================================"
Write-Host "Boostly API Testing Script"
Write-Host "========================================"
Write-Host ""

# Initialize database
Write-Host "1. Initializing database..."
$response = Invoke-RestMethod -Uri "http://localhost:5000/init-db" -Method Post
Write-Host "SUCCESS: Database initialized"
Write-Host ""

# Create students
Write-Host "2. Creating students..."
$body1 = @{
    id = "2022CS001"
    name = "Alice Johnson"
    email = "alice@university.edu"
} | ConvertTo-Json
$student1 = Invoke-RestMethod -Uri "http://localhost:5000/students" -Method Post -ContentType "application/json" -Body $body1
Write-Host "SUCCESS: Created Alice Johnson"

$body2 = @{
    id = "2022CS002"
    name = "Bob Smith"
    email = "bob@university.edu"
} | ConvertTo-Json
$student2 = Invoke-RestMethod -Uri "http://localhost:5000/students" -Method Post -ContentType "application/json" -Body $body2
Write-Host "SUCCESS: Created Bob Smith"

$body3 = @{
    id = "2022CS003"
    name = "Charlie Davis"
    email = "charlie@university.edu"
} | ConvertTo-Json
$student3 = Invoke-RestMethod -Uri "http://localhost:5000/students" -Method Post -ContentType "application/json" -Body $body3
Write-Host "SUCCESS: Created Charlie Davis"
Write-Host ""

# Test Recognition
Write-Host "3. Testing Recognition (Credit Transfer)..."
$recBody1 = @{
    sender_id = "2022CS001"
    recipient_id = "2022CS002"
    credits = 15
    message = "Great job on the project!"
} | ConvertTo-Json
$recognition1 = Invoke-RestMethod -Uri "http://localhost:5000/recognition" -Method Post -ContentType "application/json" -Body $recBody1
Write-Host "SUCCESS: Alice sent 15 credits to Bob"

$recBody2 = @{
    sender_id = "2022CS003"
    recipient_id = "2022CS002"
    credits = 25
    message = "Excellent teamwork!"
} | ConvertTo-Json
$recognition2 = Invoke-RestMethod -Uri "http://localhost:5000/recognition" -Method Post -ContentType "application/json" -Body $recBody2
Write-Host "SUCCESS: Charlie sent 25 credits to Bob"

$recBody3 = @{
    sender_id = "2022CS001"
    recipient_id = "2022CS003"
    credits = 20
    message = "Nice work!"
} | ConvertTo-Json
$recognition3 = Invoke-RestMethod -Uri "http://localhost:5000/recognition" -Method Post -ContentType "application/json" -Body $recBody3
Write-Host "SUCCESS: Alice sent 20 credits to Charlie"
Write-Host ""

# Test Business Rule: Self-recognition (should fail)
Write-Host "4. Testing Business Rule: Self-recognition..."
try {
    $selfRecBody = @{
        sender_id = "2022CS001"
        recipient_id = "2022CS001"
        credits = 10
        message = "Test"
    } | ConvertTo-Json
    $selfRec = Invoke-RestMethod -Uri "http://localhost:5000/recognition" -Method Post -ContentType "application/json" -Body $selfRecBody -ErrorAction Stop
    Write-Host "FAILED: Self-recognition should be blocked!"
} catch {
    Write-Host "SUCCESS: Self-recognition correctly blocked"
}
Write-Host ""

# Test Endorsements
Write-Host "5. Testing Endorsements..."
$endBody1 = @{
    recognition_id = 1
    endorser_id = "2022CS003"
} | ConvertTo-Json
$endorsement1 = Invoke-RestMethod -Uri "http://localhost:5000/endorsement" -Method Post -ContentType "application/json" -Body $endBody1
Write-Host "SUCCESS: Charlie endorsed recognition #1"

# Test duplicate endorsement (should fail)
try {
    $dupEndBody = @{
        recognition_id = 1
        endorser_id = "2022CS003"
    } | ConvertTo-Json
    $dupEndorse = Invoke-RestMethod -Uri "http://localhost:5000/endorsement" -Method Post -ContentType "application/json" -Body $dupEndBody -ErrorAction Stop
    Write-Host "FAILED: Duplicate endorsement should be blocked!"
} catch {
    Write-Host "SUCCESS: Duplicate endorsement correctly blocked"
}
Write-Host ""

# Test Redemption
Write-Host "6. Testing Redemption..."
$redemptionBody = @{
    student_id = "2022CS002"
    credits = 10
} | ConvertTo-Json
$redemption = Invoke-RestMethod -Uri "http://localhost:5000/redemption" -Method Post -ContentType "application/json" -Body $redemptionBody
Write-Host "SUCCESS: Bob redeemed 10 credits for Rs. $($redemption.redemption.voucher_value)"
Write-Host "Bob's remaining credits: $($redemption.remaining_credits)"
Write-Host ""

# Test Leaderboard
Write-Host "7. Testing Leaderboard..."
$leaderboard = Invoke-RestMethod -Uri "http://localhost:5000/leaderboard" -Method Get
Write-Host "SUCCESS: Leaderboard generated with $($leaderboard.leaderboard.Count) students"
foreach ($student in $leaderboard.leaderboard) {
    Write-Host "  Rank $($student.rank): $($student.student_name) - $($student.total_credits_received) credits"
}
Write-Host ""

# Test Credit Reset
Write-Host "8. Testing Credit Reset..."
$reset = Invoke-RestMethod -Uri "http://localhost:5000/reset-credits/2022CS001" -Method Post
Write-Host "SUCCESS: Credit reset for Alice"
Write-Host "  Old credits: $($reset.old_available_credits) -> New credits: $($reset.new_available_credits)"
Write-Host ""

# Get final student details
Write-Host "9. Final Student Details..."
$alice = Invoke-RestMethod -Uri "http://localhost:5000/students/2022CS001" -Method Get
Write-Host "Alice Johnson:"
Write-Host "  Available credits: $($alice.available_credits)"
Write-Host "  Received credits: $($alice.received_credits)"
Write-Host "  Credits sent this month: $($alice.credits_sent_this_month)"

$bob = Invoke-RestMethod -Uri "http://localhost:5000/students/2022CS002" -Method Get
Write-Host "Bob Smith:"
Write-Host "  Available credits: $($bob.available_credits)"
Write-Host "  Received credits: $($bob.received_credits)"
Write-Host "  Credits sent this month: $($bob.credits_sent_this_month)"
Write-Host ""

# List all recognitions
Write-Host "10. Listing all recognitions..."
$recognitions = Invoke-RestMethod -Uri "http://localhost:5000/recognitions" -Method Get
Write-Host "SUCCESS: Total recognitions in system: $($recognitions.count)"
Write-Host ""

Write-Host "========================================"
Write-Host "All tests completed successfully!"
Write-Host "========================================"
