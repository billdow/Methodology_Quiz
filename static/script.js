document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('quiz-form');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const submitBtn = document.getElementById('submit-btn');
    const progressBar = document.querySelector('.progress-bar');
    const questions = document.querySelectorAll('.question-container');
    let currentQuestion = 1;

    function updateProgress() {
        const progress = ((currentQuestion - 1) / questions.length) * 100;
        progressBar.style.width = progress + '%';
    }

    function showQuestion(questionNumber) {
        questions.forEach(q => {
            if (parseInt(q.dataset.question) === questionNumber) {
                q.classList.remove('d-none');
            } else {
                q.classList.add('d-none');
            }
        });

        prevBtn.style.display = questionNumber === 1 ? 'none' : 'inline-block';
        if (questionNumber === questions.length) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-block';
        } else {
            nextBtn.style.display = 'inline-block';
            submitBtn.style.display = 'none';
        }

        updateProgress();
    }

    nextBtn.addEventListener('click', () => {
        if (currentQuestion < questions.length) {
            currentQuestion++;
            showQuestion(currentQuestion);
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentQuestion > 1) {
            currentQuestion--;
            showQuestion(currentQuestion);
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const answers = {};
        for (let [key, value] of formData.entries()) {
            answers[key] = value;
        }

        try {
            const response = await fetch('/submit_quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(answers)
            });

            const result = await response.json();
            displayResults(result);
        } catch (error) {
            console.error('Error:', error);
        }
    });

    function displayResults(result) {
        document.getElementById('quiz-container').style.display = 'none';
        document.getElementById('results-container').style.display = 'block';
        
        const recommendedMethodology = result.recommended.charAt(0).toUpperCase() + result.recommended.slice(1);
        document.getElementById('recommended-methodology').textContent = recommendedMethodology;

        const scoresContainer = document.getElementById('methodology-scores');
        scoresContainer.innerHTML = '';
        
        for (const [methodology, score] of Object.entries(result.scores)) {
            const percentage = (score / 10) * 100;
            const methodologyDiv = document.createElement('div');
            methodologyDiv.className = 'methodology-score';
            methodologyDiv.innerHTML = `
                <div class="d-flex justify-content-between">
                    <span>${methodology.charAt(0).toUpperCase() + methodology.slice(1)}</span>
                    <span>${percentage.toFixed(1)}%</span>
                </div>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${percentage}%"></div>
                </div>
            `;
            scoresContainer.appendChild(methodologyDiv);
        }

        const descriptions = {
            waterfall: "Traditional, sequential approach best suited for projects with well-defined requirements and minimal expected changes.",
            agile: "Iterative approach ideal for projects that require flexibility and frequent stakeholder feedback.",
            DevOps: "Continuous delivery approach focusing on automation and integration between development and operations.",
            hybrid: "Mixed approach combining elements of different methodologies to best suit varying project needs."
        };

        document.getElementById('methodology-description').innerHTML = `
            <p><strong>${recommendedMethodology} Methodology:</strong> ${descriptions[result.recommended]}</p>
            <p>This recommendation is based on your responses regarding project size, requirements stability, team structure, deployment frequency, and stakeholder involvement.</p>
        `;
        window.quizResults = result;
    }

    document.getElementById('generate-report-btn').addEventListener('click', async () => {
        try {
            const response = await fetch('/generate_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(window.quizResults)
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = response.headers.get('content-disposition').split('filename=')[1];
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
            } else {
                alert('Error generating report. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error generating report. Please try again.');
        }
    });
});
