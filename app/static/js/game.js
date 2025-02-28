document.addEventListener('DOMContentLoaded', function() {
    const equationElement = document.getElementById('equation');
    const scoreElement = document.getElementById('score');
    const levelElement = document.getElementById('level');
    const timerBar = document.getElementById('timer-bar');
    const correctBtn = document.getElementById('correct-btn');
    const incorrectBtn = document.getElementById('incorrect-btn');
    
    let currentEquation = null;
    let timerId = null;
    let timerWidth = 100;
    let timerInterval = null;
    
    // Disable buttons initially
    correctBtn.disabled = true;
    incorrectBtn.disabled = true;
    
    // Load first equation
    fetchNewEquation();
    
    // Add event listeners
    correctBtn.addEventListener('click', () => checkAnswer(true));
    incorrectBtn.addEventListener('click', () => checkAnswer(false));

    function showLoading() {
        // Create a loading spinner element
        const spinner = document.createElement('div');
        spinner.className = 'spinner-border text-primary';
        spinner.role = 'status';
        spinner.innerHTML = '<span class="visually-hidden">Loading...</span>';
        
        document.body.appendChild(spinner);
    }
    
    function hideLoading() {
        const spinner = document.querySelector('.spinner-border');
        if (spinner) {
            spinner.remove();
        }
    }
    
    function fetchNewEquation() {
        showLoading(); // Show loading spinner

        // Reset UI state
        timerWidth = 100;
        timerBar.style.width = '100%';
        timerBar.className = 'progress-bar bg-success';
        
        // Disable buttons during loading
        correctBtn.disabled = true;
        incorrectBtn.disabled = true;
        equationElement.textContent = 'Loading...';
        
        // Clear any existing timer
        if (timerInterval) {
            clearInterval(timerInterval);
        }
        
        // Fetch new equation from API
        fetch('/api/equation')
            .then(response => response.json())
            .then(data => {
                hideLoading();

                currentEquation = data;
                equationElement.textContent = data.equation;
                
                // Enable buttons
                correctBtn.disabled = false;
                incorrectBtn.disabled = false;
                
                // Start timer
                startTimer(data.time_limit);
            })
            .catch(error => {
                hideLoading(); // Hide loading spinner on error
                
                console.error('Error fetching equation:', error);
                equationElement.textContent = 'Error loading equation. Please try again.';
            });
    }
    
    function startTimer(timeLimit) {
        const decrementAmount = 100 / (timeLimit * 10); // Update 10 times per second
        
        timerInterval = setInterval(() => {
            timerWidth -= decrementAmount;
            timerBar.style.width = timerWidth + '%';
            
            // Change color as time runs out
            if (timerWidth < 25) {
                timerBar.className = 'progress-bar bg-danger';
            } else if (timerWidth < 50) {
                timerBar.className = 'progress-bar bg-warning';
            }
            
            // Time's up
            if (timerWidth <= 0) {
                clearInterval(timerInterval);
                gameOver();
            }
        }, 100);
    }
    
    function checkAnswer(userAnswer) {
        // Clear timer
        if (timerInterval) {
            clearInterval(timerInterval);
        }
        
        // Disable buttons during processing
        correctBtn.disabled = true;
        incorrectBtn.disabled = true;
        
        // Send answer to server
        fetch('/api/answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                is_correct: userAnswer,
                actual_correct: currentEquation.is_correct
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.correct) {
                // Update score and level
                scoreElement.textContent = data.score;
                levelElement.textContent = data.level;
                
                // Show next equation
                fetchNewEquation();
            } else {
                // Game over
                gameOver();
            }
        })
        .catch(error => {
            console.error('Error submitting answer:', error);
            equationElement.textContent = 'Error submitting answer. Please try again.';
        });
    }
    
    function gameOver() {
        // Redirect to game over page
        window.location.href = '/game_over';
    }
});
