const questionInput = document.getElementById("question");
const askButton = document.getElementById("askButton");

const loading = document.getElementById("loading");
const error = document.getElementById("error");

const answerSection = document.getElementById("answerSection");

const answer = document.getElementById("answer");
const evidence = document.getElementById("evidence");

const book = document.getElementById("book");
const author = document.getElementById("author");

askButton.addEventListener("click", async () => {

    const question = questionInput.value.trim();

    if (!question) {
        error.textContent = "Please enter a question.";
        error.classList.remove("hidden");
        return;
    }

    error.classList.add("hidden");
    answerSection.classList.add("hidden");

    loading.classList.remove("hidden");
    askButton.disabled = true;

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/ask",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: question
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Something went wrong."
            );
        }

        answer.textContent = data.answer;

        evidence.textContent =
            data.evidence || "No evidence available.";

        book.textContent =
            data.book || "Not identified";

        author.textContent =
            data.author || "Not identified";

        answerSection.classList.remove("hidden");

    } catch (err) {

        error.textContent =
            "Error: " + err.message;

        error.classList.remove("hidden");

    } finally {

        loading.classList.add("hidden");
        askButton.disabled = false;
    }
});