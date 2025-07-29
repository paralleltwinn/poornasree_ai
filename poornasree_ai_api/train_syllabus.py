import asyncio
import os
from enhanced_service_guide_trainer import EnhancedServiceGuideTrainer

async def train_syllabus():
    trainer = EnhancedServiceGuideTrainer()
    
    # Check current directory and file existence
    current_dir = os.getcwd()
    file_name = 'Training syllabus\xa0and documents.xlsx'  # Use the actual filename with non-breaking space
    file_path = os.path.join(current_dir, file_name)
    
    print(f'Current directory: {current_dir}')
    print(f'Looking for file: {repr(file_name)}')  # Show the actual characters
    print(f'Full path: {file_path}')
    print(f'File exists: {os.path.exists(file_path)}')
    
    if os.path.exists(file_path):
        print(f'Training file: {file_path}')
        result = await trainer.train_excel_service_guide(file_path)
        
        if result['success']:
            print(f'✅ Successfully trained syllabus document!')
            print(f'📊 Entries trained: {result["entries_trained"]}')
            print(f'🧠 Knowledge base entries: {result["knowledge_base_entries"]}')
            
            summary = result['training_summary']
            print(f'📋 By Type: {summary["types"]}')
            print(f'📂 By Category: {summary["categories"]}')
            print(f'📄 By Sheet: {summary["sheets"]}')
            
            # Show sample entry
            if result['sample_entries']:
                sample = result['sample_entries'][0]
                print(f'\n📋 Sample Entry:')
                print(f'   Title: {sample["title"]}')
                print(f'   Type: {sample["type"]} | Category: {sample["category"]}')
                print(f'   Keywords: {", ".join(sample["keywords"][:5])}...')
        else:
            print(f'❌ Training failed: {result.get("error")}')
    else:
        print(f'❌ File not found: {file_path}')

if __name__ == "__main__":
    asyncio.run(train_syllabus())
