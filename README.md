# Land Compensation Support System (LCSS)

The Land Compensation Support System is designed to make land compensation processing easier, faster, and more organized.  
It helps manage landowner details, calculate compensation amounts, and validate supporting documents using basic computer vision techniques.

## Technology Stack Used
- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Python  
- **Database:** MySQL  
- **Computer Vision:** OpenCV (for document/image validation)  
- **Tools:** Git, GitHub, GitHub Desktop  

## Computer Vision Involvement
Basic computer vision is used to:
- Read and validate uploaded land-related documents  
- Check image clarity and format  
- Extract or verify key details using preprocessing techniques  

This increases accuracy and reduces chances of incorrect or unclear document submissions.

## How the System Works
1. The user enters landowner details and uploads supporting documents.  
2. Computer vision processes the uploaded documents to ensure they are clear and valid for further analysis.  
3. The backend receives the cleaned and validated data.  
4. The system calculates the compensation amount based on predefined rules or parameters.  
5. All records are stored in the MySQL database for future reference and updates.  
6. The user can view, update, or verify details anytime through the interface.

## Key Features
- Manage landowner and land-related details  
- Validate uploaded documents using computer vision  
- Automatic compensation calculation  
- Clean and simple interface  
- Database storage for long-term record management  
