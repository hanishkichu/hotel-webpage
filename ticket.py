import streamlit as st
import qrcode
import io
import random
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, DECIMAL
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import datetime

Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    
    bookings = relationship("Booking", back_populates="user")

class Booking(Base):
    __tablename__ = 'booking'
    booking_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    show_id = Column(Integer, ForeignKey('show.show_id'))
    booking_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    total_cost = Column(DECIMAL, nullable=False)
    
    user = relationship("User", back_populates="bookings")

class Movie(Base):
    __tablename__ = 'movie'
    movie_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    rating = Column(String, nullable=False)

class Show(Base):
    __tablename__ = 'show'
    show_id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movie.movie_id'))
    show_datetime = Column(DateTime, nullable=False)

    movie = relationship("Movie")

# Streamlit UI
st.title("🎭 Welcome to Unox Multiplex 🎬")

def login_page():
    choice = st.radio("Select an option", ["Login", "Register"])
    
    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("Login Successful!")
            st.rerun()
    
    elif choice == "Register":
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Register"):
            st.success("Registration successful! You can now log in.")

if "logged_in" not in st.session_state:
    login_page()
else:
    def ticket_booking_page():
        st.title(f"🍿🎬 Unox Multiplex Ticket Booking - Welcome {st.session_state['username']}")

        movies = {
            "Avengers": [{"screen": "Gold", "time": "10:00 AM", "seats": 150, "price": 500},
                         {"screen": "Silver", "time": "1:30 PM", "seats": 200, "price": 300}],
        }

        movie_choice = st.selectbox("Select a Movie", list(movies.keys()))

        if movie_choice:
            show_choice = st.selectbox(
                "Select a Show", 
                [f"{show['screen']} - {show['time']} (Rs. {show['price']}/ticket)" for show in movies[movie_choice]]
            )
            
            show_details = next(show for show in movies[movie_choice] if f"{show['screen']} - {show['time']} (Rs. {show['price']}/ticket)" == show_choice)
            seats = st.number_input("Select Number of Seats", min_value=1, max_value=show_details["seats"], step=1)
            total_cost = seats * show_details["price"]

            if st.button("Book Ticket & Generate Payment QR"):
                payment_qr_code = qrcode.make(f"Amount: Rs. {total_cost} | Status: Pending")
                img_io = io.BytesIO()
                payment_qr_code.save(img_io, format='PNG')
                img_io.seek(0)
                st.success(f"📢 Scan the QR Code to Complete Payment. Total Cost: Rs. {total_cost}")
                st.image(img_io)
    
    ticket_booking_page()
