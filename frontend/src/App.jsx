import React, { useState } from "react";
import axios from "axios";

function App() {
  const [link, setLink] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleLinkSubmit = async () => {
    try {
      await axios.post("http://localhost:8000/process_link/", { youtube_url: link });
      alert("Video processed successfully! Now you can ask questions.");
    } catch (error) {
      console.error(error);
      alert("Failed to process video.");
    }
  };

  const handleQuestionSubmit = async () => {
    try {
      const res = await axios.post("http://localhost:8000/ask/", { question: question });
      setAnswer(res.data.answer);
    } catch (error) {
      console.error(error);
      alert("Failed to fetch answer.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h1 className="text-3xl font-bold mb-6">🎥 YouTube RAG App</h1>

      <input
        type="text"
        placeholder="Paste YouTube URL..."
        value={link}
        onChange={(e) => setLink(e.target.value)}
        className="border p-2 w-80 mb-4 rounded"
      />
      <button onClick={handleLinkSubmit} className="bg-blue-500 text-white px-4 py-2 rounded mb-8">
        Process Video
      </button>

      <input
        type="text"
        placeholder="Ask a question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        className="border p-2 w-80 mb-4 rounded"
      />
      <button onClick={handleQuestionSubmit} className="bg-green-500 text-white px-4 py-2 rounded">
        Ask
      </button>

      {answer && (
        <div className="mt-8 bg-white p-4 rounded shadow w-3/4">
          <h2 className="text-xl font-semibold mb-2">Answer:</h2>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default App;
