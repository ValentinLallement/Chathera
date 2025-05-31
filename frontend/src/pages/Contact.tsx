const Contact = () => {
  return (
    <div className="contact-page">
      <h1>Contact Us</h1>
      <div className="contact-content">
        <p>Get in touch with our team</p>
        <form className="contact-form">
          <input type="email" placeholder="Your email" />
          <textarea placeholder="Your message"></textarea>
          <button type="submit">Send Message</button>
        </form>
      </div>
    </div>
  );
};

export default Contact;
