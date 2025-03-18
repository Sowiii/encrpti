import pickle

try:
    with open("authorized_faces.pkl", "rb") as file:
        data = pickle.load(file)
        print("✅ Contents of authorized_faces.pkl:", data)
except FileNotFoundError:
    print("❌ Error: authorized_faces.pkl not found!")
except Exception as e:
    print(f"❌ Error: {e}")
