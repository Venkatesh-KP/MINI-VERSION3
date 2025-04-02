function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    const chatLog = document.getElementById("chat-log");

    if (userInput.trim() === "") return;

    // Add user message to the chat log
    const userMessage = document.createElement("div");
    userMessage.textContent = "You: " + userInput;
    chatLog.appendChild(userMessage);

    // Clear the input field
    document.getElementById("user-input").value = "";

    // Simulate a response from the chatbot
    setTimeout(function() {
        const botMessage = document.createElement("div");
        botMessage.textContent = "Bot: " + getBotResponse(userInput);
        chatLog.appendChild(botMessage);

        // Scroll to the bottom of the chat log
        chatLog.scrollTop = chatLog.scrollHeight;
    }, 1000);  // Simulate a slight delay
}

function getBotResponse(input) {
    // Placeholder for actual student information retrieval logic
    const responses = {
        "name": "The student's name is John Doe.",
        "age": "The student is 21 years old.",
        "major": "The student is majoring in Computer Science.",
        "graduation": "The student is expected to graduate in 2025."
    };

    // Return a response based on input or default message
    for (let key in responses) {
        if (input.toLowerCase().includes(key)) {
            return responses[key];
        }
    }

    return "Sorry, I don't have information on that.";
}
