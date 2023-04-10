import React, { useState, useEffect, useRef } from 'react';
import { BsFillGearFill } from "react-icons/bs"
import axios from 'axios';
import './App.css';
var Convert = require('ansi-to-html');
var convert = new Convert({newline: true});




function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const [currentThought, setCurrentThought] = useState(null);
  const [thought, setThought] = useState(null);
  const [isThoughtVisible, setIsThoughtVisible] = useState(false);


  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = async () => {
    if (input.trim() === '') return;

    setMessages([...messages, { text: input, user: 'You' }]);
    setInput('');

    try {
      setLoading(true);
      const response = await axios.get("http://127.0.0.1:7860/predict", {
        params: { message: input },
      });
    
      const answer = response.data.response;
      const movies = response.data.movies;
      const thought = response.data.thought;

      setThought(thought);
      setIsThoughtVisible(false);
    
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          text: answer,
          user: "Agent",
          movies: movies,
          thought: thought,
        },
      ]);
    } catch (error) {
      console.error("Error fetching message:", error);
    } finally {
      setLoading(false);
    }
  };
  
  const ThoughtModal = ({ show, onClose, thought }) => {
    if (!show) {
      return null;
    }
  
    return (
      <div className="thought-modal">
        <div className="thought-modal-content">
          {/* <h3>Bot's Thought</h3> */}
          <div dangerouslySetInnerHTML={{__html: convert.toHtml(thought)}} />
          <button className="close-modal-button" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    );

  };


  const MovieCard = ({ movie }) => {
    const { title, year, directors, Overview, Poster, genre } = movie;
  
    return (
      <div className="movie-card">
        <div className="movie-top-section">
          <div className="movie-cover-container">
            <img src={Poster} alt={title} className="movie-cover" />
          </div>
          <div className="movie-details">
            <h4>{title}</h4>
            <p>{year}</p>
            <p>{directors.join(', ')}</p>
          </div>
        </div>
        <p className="genre">{genre.join(', ')}</p>
        <p className="synopsis">{Overview}</p>
        <button className="watch-now-button">Watch Now</button>
      </div>
    );
  };
  

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className="App">
      <ThoughtModal
        show={currentThought !== null}
        onClose={() => setCurrentThought(null)}
        thought={currentThought}
      />
      <div className="chat-container">
        <div className="chat-box">
          <div className="messages">
            {messages.map((message, index) => (
              <React.Fragment key={index}>
                <div
                  className={`${
                    message.user === "You"
                      ? "message-user-container"
                      : "message-bot-container"
                  }`}
                >
                  <div
                    className={`message ${
                      message.user === "You" ? "message-user" : "message-bot"
                    }`}
                  >
                    <span className="user"></span>
                    {message.text}
                    {message.user === "Agent" && message.thought && (
                    <button
                      className="toggle-thought-button"
                      onClick={() => setCurrentThought(message.thought)}
                    >
                      <BsFillGearFill />
                    </button>
                )}
                  </div>
                  
                </div>

                {message.movies && message.movies.length > 0 && (
                  <div className="movie-cards-container">
                    {message.movies.map((movie) => (
                      <MovieCard key={movie.title} movie={movie} />
                    ))}
                  </div>
                )}
              </React.Fragment>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <div className="input-container">
            <input
              type="text"
              className="input"
              value={loading ? 'Thinking...' : input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
            />
            <button className="send-button" onClick={sendMessage} disabled={loading}>
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
  
  
}

export default App;
