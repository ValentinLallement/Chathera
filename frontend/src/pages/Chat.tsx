const Chat = () => {
  return (
    <div className="chat-page">
      <h1>Chat</h1>
      <div className="chat-container">
        <div className="chat-sidebar">
          <h2>Conversations</h2>
          <div className="conversation-list">
            <p>No conversations yet</p>
          </div>
        </div>
        <div className="chat-main">
          <div className="messages">
            <p className="welcome-message">Start a new conversation!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
