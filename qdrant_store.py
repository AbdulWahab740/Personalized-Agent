# 🛠️ WINDOWS TENSORFLOW FIX & LIGHTWEIGHT ALTERNATIVE
# This fixes your current issue and sets up lightweight deployment

import os
import sys
import subprocess
import json
from typing import Dict, List, Any
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

load_dotenv()

# 🚨 IMMEDIATE FIX: Skip Heavy Dependencies Completely

class LightweightEmbeddingGenerator:
    """
    Lightweight version that bypasses sentence-transformers entirely
    Uses Hugging Face Inference API instead of local models
    """
    
    def __init__(self, profile_file: str = "profile_data.json"):
        self.profile_file = profile_file
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY") 
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        
        # Initialize Qdrant client (lightweight)
        self.qdrant_client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key
        )
        
        # HF API endpoint for feature extraction
        self.hf_api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-mpnet-base-v2"
        
        print("✅ Lightweight Embedding Generator initialized (NO heavy dependencies!)")
    
    def get_embedding_from_hf(self, text: str, retries: int = 2) -> List[float]:
        """Get embedding using Hugging Face Inference API"""
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        
        for attempt in range(retries):
            try:
                response = requests.post(
                    self.hf_api_url,
                    headers=headers,
                    json={"inputs": text},
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Handle different response formats
                    if isinstance(result, list) and len(result) > 0:
                        if isinstance(result[0], list):
                            embedding = result[0]  # Nested list format
                        else:
                            embedding = result  # Flat list format
                    else:
                        embedding = result
                    return embedding
                elif response.status_code == 503:
                    print(f"⏳ Model loading, waiting 30 seconds... (attempt {attempt + 1})")
                    import time
                    time.sleep(30)
                    continue
                else:
                    print(f"❌ HF API error: {response.status_code} - {response.text}")
                    return None
                    
            except Exception as e:
                print(f"❌ Error calling HF API (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    import time
                    time.sleep(10)
        
        return None
    
    def load_personal_data(self) -> Dict[str, Any]:
        """Load personal profile data"""
        if not os.path.exists(self.profile_file):
            print(f"❌ Profile file {self.profile_file} not found!")
            print("💡 Create it with your personal data. Example structure:")
            example = {
                "name": "Your Name",
                "email": "your.email@example.com",
                "about": "Your professional bio...",
                "skills": ["Python", "FastAPI", "AI/ML"],
                "achievements": ["Built AI agent system"],
                "projects": [{"title": "AI Agent", "description": "Personal content agent"}],
                "linkedin_posts": [{"title": "My Journey", "content": "Building AI..."}]
            }
            with open("profile_data_example.json", "w") as f:
                json.dump(example, f, indent=2)
            print(f"📄 Created profile_data_example.json - rename and fill it out!")
            return {}
        
        with open(self.profile_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def prepare_documents(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare documents for embedding (same logic as before)"""
        documents = []
        
        # Basic info
        basic_info = f"Name: {profile_data.get('name', 'N/A')}, Email: {profile_data.get('email', 'N/A')}"
        documents.append({"content": basic_info, "metadata": {"type": "basic_info"}})
        
        # About
        if profile_data.get('about'):
            documents.append({"content": f"About: {profile_data['about']}", "metadata": {"type": "about"}})
        
        # Skills
        skills = profile_data.get('skills', [])
        if skills:
            documents.append({"content": f"Skills: {', '.join(skills)}", "metadata": {"type": "skills"}})
        
        # Achievements
        for i, achievement in enumerate(profile_data.get('achievements', [])):
            documents.append({
                "content": f"Achievement: {achievement}",
                "metadata": {"type": "achievement", "index": i}
            })
        
        # Projects
        for i, project in enumerate(profile_data.get('projects', [])):
            content = f"Project: {project.get('title', 'Untitled')} - {project.get('description', 'No description')}"
            documents.append({
                "content": content,
                "metadata": {"type": "project", "index": i, "title": project.get('title', 'Untitled')}
            })
        
        # LinkedIn posts
        for i, post in enumerate(profile_data.get('linkedin_posts', [])):
            content = f"LinkedIn Post: {post.get('title', 'Untitled')} - {post.get('content', 'No content')}"
            documents.append({
                "content": content,
                "metadata": {"type": "linkedin_post", "index": i}
            })
        
        return documents
    
    def process_and_upload(self, collection_name: str = "personal_info", batch_size: int = 5):
        """Complete pipeline using HF API instead of local models"""
        print("🚀 Starting lightweight processing pipeline...")
        
        # Load data
        profile_data = self.load_personal_data()
        if not profile_data:
            return False
        
        print(f"✅ Loaded profile for: {profile_data.get('name', 'Unknown')}")
        
        # Prepare documents
        documents = self.prepare_documents(profile_data)
        print(f"✅ Prepared {len(documents)} documents")
        
        # Generate embeddings using HF API
        print("🔄 Generating embeddings via Hugging Face API...")
        enriched_documents = []
        
        for i, doc in enumerate(documents):
            print(f"  Processing {i+1}/{len(documents)}: {doc['metadata']['type']}")
            
            embedding = self.get_embedding_from_hf(doc['content'])
            if embedding is None:
                print(f"❌ Failed to get embedding for document {i+1}")
                continue
            
            enriched_doc = {
                "id": i + 1,
                "content": doc['content'],
                "metadata": doc['metadata'],
                "embedding": embedding
            }
            enriched_documents.append(enriched_doc)
            
            # Add small delay to respect rate limits
            import time
            time.sleep(1)
        
        if not enriched_documents:
            print("❌ No documents processed successfully!")
            return False
        
        print(f"✅ Generated {len(enriched_documents)} embeddings")
        
        # Upload to Qdrant
        try:
            # Delete existing collection
            try:
                self.qdrant_client.delete_collection(collection_name)
                print(f"🗑️ Deleted existing collection: {collection_name}")
            except:
                pass
            
            # Create new collection
            vector_size = len(enriched_documents[0]['embedding'])
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            print(f"✅ Created collection: {collection_name} (dimension: {vector_size})")
            
            # Upload points
            points = []
            for doc in enriched_documents:
                point = PointStruct(
                    id=doc['id'],
                    vector=doc['embedding'],
                    payload={'content': doc['content'], 'metadata': doc['metadata']}
                )
                points.append(point)
            
            self.qdrant_client.upsert(collection_name=collection_name, points=points)
            print(f"✅ Uploaded {len(points)} documents to Qdrant!")
            
            # Verify
            collection_info = self.qdrant_client.get_collection(collection_name)
            print(f"📊 Collection has {collection_info.points_count} points")
            
            return True
            
        except Exception as e:
            print(f"❌ Qdrant upload error: {e}")
            return False


# 🔧 WINDOWS TENSORFLOW FIX (if you want to keep using heavy models)

def fix_tensorflow_windows():
    """Fix TensorFlow on Windows"""
    print("🔧 Attempting to fix TensorFlow on Windows...")
    
    fixes = [
        "pip uninstall tensorflow tensorflow-cpu -y",
        "pip install tensorflow-cpu==2.13.0",  # Known stable version
        "pip install --upgrade setuptools",
        "pip install microsoft-visual-cpp-build-tools",  # Sometimes needed
    ]
    
    print("💡 Try these commands in order:")
    for i, fix in enumerate(fixes, 1):
        print(f"  {i}. {fix}")
    
    print("\n🔄 Or create a fresh environment:")
    print("  conda create -n ai_agent python=3.9")
    print("  conda activate ai_agent")
    print("  pip install tensorflow-cpu==2.13.0")
    print("  pip install sentence-transformers")


# 🚀 MAIN EXECUTION

def main():
    """Main execution with multiple options"""
    print("🚨 TensorFlow/sentence-transformers issue detected!")
    print("\n🎯 Choose your approach:")
    print("1. ✨ Use lightweight HF API approach (RECOMMENDED)")
    print("2. 🔧 Try to fix TensorFlow on Windows") 
    print("3. 🐍 Create fresh conda environment")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        print("\n✨ Using lightweight Hugging Face API approach...")
        
        # Check if .env file exists
        if not os.path.exists('.env'):
            print("❌ .env file not found!")
            print("💡 Create .env with:")
            print("HUGGINGFACE_TOKEN=your_token_here")
            print("QDRANT_URL=your_qdrant_url")
            print("QDRANT_API_KEY=your_qdrant_key")
            print("\n🔑 Get HF token: https://huggingface.co/settings/tokens")
            print("🔑 Get Qdrant: https://cloud.qdrant.io/")
            return
        
        # Run lightweight processor
        processor = LightweightEmbeddingGenerator()
        success = processor.process_and_upload()
        
        if success:
            print("\n🎉 Success! Your personal data is now in Qdrant Cloud")
            print("💡 You can now deploy with lightweight requirements")
        else:
            print("\n❌ Processing failed. Check your API keys and try again.")
    
    elif choice == "2":
        fix_tensorflow_windows()
    
    elif choice == "3":
        print("\n🐍 Create fresh conda environment:")
        print("1. Install Miniconda: https://docs.conda.io/en/latest/miniconda.html")
        print("2. conda create -n ai_agent python=3.9")
        print("3. conda activate ai_agent")
        print("4. pip install qdrant-client requests python-dotenv")
        print("5. pip install sentence-transformers  # Try this last")
    
    else:
        print("Invalid choice!")


# 💾 CREATE MINIMAL REQUIREMENTS FILE

def create_minimal_requirements():
    """Create minimal requirements.txt that avoids the TensorFlow issue"""
    minimal_reqs = """
# Minimal requirements - NO TensorFlow/PyTorch dependencies
qdrant-client==1.7.0
requests==2.31.0
python-dotenv==1.0.0
fastapi==0.104.1
uvicorn==0.24.0
langchain==0.0.350
streamlit==1.28.0
pandas==2.1.3

# For development/testing only (optional)
# openai==1.3.0
# anthropic>=0.5.0
"""
    
    with open("requirements_minimal.txt", "w") as f:
        f.write(minimal_reqs.strip())
    
    print("✅ Created requirements_minimal.txt")
    print("💡 Use: pip install -r requirements_minimal.txt")


if __name__ == "__main__":
    # Check if we're in the error scenario
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers working fine!")
        main()
    except ImportError as e:
        if "tensorflow" in str(e).lower() or "dll" in str(e).lower():
            print("🚨 TensorFlow/DLL issue detected - using lightweight approach!")
            main()
        else:
            print(f"❌ Import error: {e}")
    