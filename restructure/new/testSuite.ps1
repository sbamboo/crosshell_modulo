param (
    [int]$times = 5
)

function RoundNumber {
    param (
        [double]$number
    )

    if ($number -is [decimal] -or $number -is [float]) {
        # Round to two decimal places if it has decimal places
        $rounded = [math]::Round($number, 2)
    } else {
        # Round to the nearest integer if it doesn't have decimal places
        $rounded = [math]::Round($number)
    }

    return $rounded
}

function RunTest {
    # Run crosshell to fix pip-deps
    python3 .\testSuite_pre.py
    # Run that inits and exports
    $first_ms = Measure-Command {python3 .\testSuite_first.py}
    # Run that dosen't init and instead imports
    $second_ms = Measure-Command {python3 .\testSuite_second.py}

    # Clean up
    $file = "test.session"
    if (Test-Path $file) {
        Remove-Item $file
    }

    $timeDiff = [int]$first_ms.TotalMilliseconds - [int]$second_ms.TotalMilliseconds

    # Get result
    return $timeDiff
}

$array = @()

Write-Output "Running test $($times) times..."

# Loop 5 times
for ($i = 1; $i -le $times; $i++) {
    # Call the function and add the result to the array
    $array += RunTest
    $proc = RoundNumber -number $( ($i/$times)*100 )
    Write-Output "Ran test $($i)/$($times), ($($proc)%)"
}

$sum = $array | Measure-Object -Sum | Select-Object -ExpandProperty Sum
$average = $sum / $array.Count

Write-Output "`nAverage time-diff: $($average)ms.`nThus importing from session rather then initing is on average $($average)ms faster."

# Clean up
$file = "test.session"
if (Test-Path $file) {
    Remove-Item $file
}