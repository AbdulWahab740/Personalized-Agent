# 1️⃣ Step 1 — Personalization Memory Setup
# Store Personal Data in Vector DB (Qdrant) as a single comprehensive profile
# This includes bio, skills, achievements, projects, LinkedIn posts, and writing style

from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import socket
import json

load_dotenv()

class PersonalInfo:
    """
    Personal Information Agent that stores and retrieves personal data
    as a single comprehensive profile for personalized content generation
    """
    
    def __init__(self, collection_name: str = "personal_info", profile_file: str = "profile_data.json"):
        self.collection_name = collection_name
        self.profile_file = profile_file
        model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        # Initialize Qdrant vector store
        self.vector_store = self._init_vector_store()
        
        # Single comprehensive personal profile
        self.personal_profile = {}
        
        # Automatically load profile data from JSON file
        self._load_profile_from_json()
    
    def _load_profile_from_json(self):
        """Load profile data from JSON file automatically"""
        try:
            if os.path.exists(self.profile_file):
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                
                # Set the loaded profile
                self.set_personal_profile(profile_data)
                print(f"✅ Profile data loaded from {self.profile_file}")
            else:
                print(f"⚠️ Profile file {self.profile_file} not found. Please create it or use set_personal_profile() manually.")
        except Exception as e:
            print(f"❌ Error loading profile from {self.profile_file}: {e}")
            print("Please check the JSON format or use set_personal_profile() manually.")
    
    def _check_qdrant_connectivity(self) -> bool:
        """Check if Qdrant server is accessible"""
        try:
            host = self.qdrant_url.replace("http://", "").replace("https://", "").split(":")[0]
            port = int(self.qdrant_url.split(":")[-1]) if ":" in self.qdrant_url else 6333
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ Qdrant server is accessible at {host}:{port}")
                return True
            else:
                print(f"❌ Cannot connect to Qdrant at {host}:{port}")
                return False
        except Exception as e:
            print(f"❌ Error checking Qdrant connectivity: {e}")
            return False

    def _init_vector_store(self) -> QdrantVectorStore:
        """Initialize Qdrant vector store"""
        # First check if Qdrant is accessible
        if not self._check_qdrant_connectivity():
            print("⚠️ Qdrant server not accessible. Continuing without vector store functionality.")
            print("💡 To use vector store features:")
            print("   1. Install Docker: https://docs.docker.com/get-docker/")
            print("   2. Start Qdrant: docker run -p 6333:6333 qdrant/qdrant")
            print("   3. Or use Qdrant Cloud: https://cloud.qdrant.io/")
            return None
        
        try:
            # Try to connect to existing collection first
            try:
                # Use the correct QdrantVectorStore constructor parameters
                vector_store = QdrantVectorStore(
                    collection_name=self.collection_name,
                    url=self.qdrant_url,
                    api_key=self.qdrant_api_key
                )
                print(f"✅ Connected to existing Qdrant collection: {self.collection_name}")
                return vector_store
            except Exception as e:
                print(f"⚠️ Could not connect to existing collection: {e}")
                print("🔄 Creating new collection...")
                
                # Create new collection with a minimal document
                minimal_doc = Document(
                    page_content="Profile initialization",
                    metadata={"type": "init", "timestamp": datetime.now().isoformat()}
                )
                
                # Use from_documents with correct parameters
                if self.qdrant_api_key:
                    vector_store = QdrantVectorStore.from_documents(
                        documents=[minimal_doc],
                        embedding=self.embeddings,
                        url=self.qdrant_url,
                        api_key=self.qdrant_api_key,
                        collection_name=self.collection_name
                    )
                else:
                    vector_store = QdrantVectorStore.from_documents(
                        documents=[minimal_doc],
                        embedding=self.embeddings,
                        url=self.qdrant_url,
                        collection_name=self.collection_name
                    )
                
                print(f"✅ New Qdrant collection created: {self.collection_name}")
                return vector_store
                
        except Exception as e:
            print(f"❌ Error initializing Qdrant: {e}")
            print("⚠️ Continuing without vector store functionality")
            print("💡 To use vector store features, make sure Qdrant is running on your system")
            print("   You can start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")
            return None
    
    def set_personal_profile(self, profile_data: Dict[str, Any]):
        """
        Set or update the complete personal profile
        This replaces any existing profile with new comprehensive data
        """
        # Store the profile data
        self.personal_profile = profile_data
        
        # Only add to vector store if it's properly initialized
        if self.vector_store is None:
            print("⚠️ Vector store not available. Profile stored locally only.")
            return
        
        # Create a comprehensive document for the vector store
        profile_content = f"""Personal Profile:

Basic Information:
- Name: {profile_data.get('name', 'N/A')}
- Email: {profile_data.get('email', 'N/A')}
- LinkedIn: {profile_data.get('linkedin_url', 'N/A')}
- GitHub: {profile_data.get('github_url', 'N/A')}

About:
{profile_data.get('about', 'N/A')}

Skills:
{', '.join(profile_data.get('skills', []))}

Achievements:
{chr(10).join([f"• {achievement}" for achievement in profile_data.get('achievements', [])])}

Projects:
{chr(10).join([f"• {project.get('title', 'Untitled')}: {project.get('description', 'No description')}" for project in profile_data.get('projects', [])])}

LinkedIn Posts (Writing Style Examples):
{chr(10).join([f"---\n{post.get('title', 'Untitled')}: {post.get('content', 'No content')}" for post in profile_data.get('linkedin_posts', [])])}

Writing Style Notes:
{profile_data.get('writing_style_notes', 'N/A')}"""
        
        # Create document for vector store
        profile_doc = Document(
            page_content=profile_content,
            metadata={
                "type": "comprehensive_profile",
                "timestamp": datetime.now().isoformat(),
                "name": profile_data.get('name', 'Unknown'),
                "last_updated": datetime.now().isoformat()
            }
        )
        
        # Add the new profile document to vector store
        try:
            # Add the new profile document
            self.vector_store.add_documents([profile_doc])
            print("✅ Comprehensive personal profile added to vector store")
            print(f"📄 Document content length: {len(profile_content)} characters")
            
            # Note: In a production environment, you might want to implement
            # proper collection clearing to remove old documents
            print("💡 Profile document added successfully. Old documents may still exist.")
            
        except Exception as e:
            print(f"❌ Error adding profile to vector store: {e}")
            print("🔍 Debug info:")
            print(f"   - Vector store type: {type(self.vector_store)}")
            print(f"   - Document content preview: {profile_content[:100]}...")
            print(f"   - Profile data keys: {list(profile_data.keys())}")
    
    def reload_profile(self):
        """Reload profile data from JSON file"""
        print(f"🔄 Reloading profile from {self.profile_file}...")
        self._load_profile_from_json()
    
    def search_personal_info(self, query: str, limit: int = 5) -> List[Document]:
        """Search personal information in the vector store"""
        if self.vector_store is None:
            print("⚠️ Vector store not available. Cannot perform search.")
            return []
        
        try:
            # First, let's check what's in the vector store
            print(f"🔍 Searching for: '{query}'")
            print(f"📊 Vector store collection: {self.collection_name}")
            
            results = self.vector_store.similarity_search(query, k=limit)
            print(f"✅ Found {len(results)} relevant results")
            
            # Show preview of results
            for i, doc in enumerate(results):
                print(f"   Result {i+1}: {doc.page_content[:100]}...")
                print(f"   Metadata: {doc.metadata}")
            
            return results
        except Exception as e:
            print(f"❌ Error searching personal info: {e}")
            return []
    
    def check_vector_store_contents(self) -> None:
        """Check what documents are currently in the vector store"""
        if self.vector_store is None:
            print("⚠️ Vector store not available.")
            return
        
        try:
            # Try to get all documents (this might not work with all Qdrant setups)
            print(f"🔍 Checking vector store contents for collection: {self.collection_name}")
            
            # Use a very broad search to see what's available
            results = self.vector_store.similarity_search("", k=10)
            print(f"📊 Found {len(results)} documents in vector store")
            
            for i, doc in enumerate(results):
                print(f"   Document {i+1}:")
                print(f"     Content preview: {doc.page_content[:150]}...")
                print(f"     Metadata: {doc.metadata}")
                print()
                
        except Exception as e:
            print(f"❌ Error checking vector store contents: {e}")
            print("💡 This might be normal for some Qdrant configurations")
    
    def get_personal_summary(self) -> str:
        """Get a comprehensive summary of the personal profile"""
        if not self.personal_profile:
            return "No personal profile found. Please set your profile first using set_personal_profile()."
        
        profile = self.personal_profile
        
        summary = "Personal Profile Summary:\n" + "="*50 + "\n\n"
        summary += f"👤 Name: {profile.get('name', 'N/A')}\n"
        summary += f"📧 Email: {profile.get('email', 'N/A')}\n"
        summary += f"🔗 LinkedIn: {profile.get('linkedin_url', 'N/A')}\n"
        summary += f"💻 GitHub: {profile.get('github_url', 'N/A')}\n\n"
        
        summary += f"📝 About:\n{profile.get('about', 'N/A')}\n\n"
        
        if profile.get('skills'):
            summary += f"🛠️ Skills ({len(profile['skills'])}): {', '.join(profile['skills'][:10])}{'...' if len(profile['skills']) > 10 else ''}\n\n"
        
        if profile.get('achievements'):
            summary += f"🏆 Achievements ({len(profile['achievements'])}): {', '.join(profile['achievements'][:5])}{'...' if len(profile['achievements']) > 5 else ''}\n\n"
        
        if profile.get('projects'):
            summary += f"🚀 Projects ({len(profile['projects'])}): {', '.join([p.get('title', 'Untitled') for p in profile['projects'][:5]])}{'...' if len(profile['projects']) > 5 else ''}\n\n"
        
        if profile.get('linkedin_posts'):
            summary += f"📱 LinkedIn Posts: {len(profile['linkedin_posts'])} posts stored\n\n"
        
        if profile.get('writing_style_notes'):
            summary += f"✍️ Writing Style: {profile['writing_style_notes'][:100]}...\n\n"
        
        summary += f"🕒 Last Updated: {profile.get('last_updated', 'N/A')}\n"
        
        return summary
