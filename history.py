"""
History Manager - Saves analysis results to CSV
No database required!
"""

import pandas as pd
import os
from datetime import datetime
import json
import uuid

HISTORY_FILE = 'history.csv'

def init_history():
    """Create history CSV if it doesn't exist"""
    if not os.path.exists(HISTORY_FILE):
        df = pd.DataFrame(columns=[
            'id', 'timestamp', 'title', 'content', 'source_type',
            'prediction', 'credibility_score', 'fake_prob', 'real_prob',
            'red_flags', 'is_deleted'
        ])
        df.to_csv(HISTORY_FILE, index=False)
        print(f"✓ Created {HISTORY_FILE}")

def save_analysis(
    title: str,
    content: str,
    source_type: str,
    prediction: str,
    credibility_score: float,
    fake_prob: float,
    real_prob: float,
    red_flags: list
) -> str:
    """Save a single analysis result to CSV"""
    init_history()
    
    new_record = {
        'id': str(uuid.uuid4())[:8],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'title': title[:200] if title else 'Untitled',
        'content': content[:500] if content else '',
        'source_type': source_type,
        'prediction': prediction,
        'credibility_score': round(credibility_score, 2),
        'fake_prob': round(fake_prob, 2),
        'real_prob': round(real_prob, 2),
        'red_flags': json.dumps(red_flags) if red_flags else '[]',
        'is_deleted': False
    }
    
    df = pd.read_csv(HISTORY_FILE)
    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)
    
    return new_record['id']

def get_history(limit: int = 50, filter_type: str = 'all'):
    """Get analysis history from CSV"""
    if not os.path.exists(HISTORY_FILE):
        init_history()
        return []
    
    df = pd.read_csv(HISTORY_FILE)
    df = df[df['is_deleted'] != True]
    
    if filter_type != 'all':
        df = df[df['source_type'] == filter_type]
    
    df = df.sort_values('timestamp', ascending=False)
    df = df.head(limit)
    
    records = df.to_dict('records')
    
    for record in records:
        try:
            record['red_flags'] = json.loads(record['red_flags'])
        except:
            record['red_flags'] = []
    
    return records

def get_history_stats():
    """Get summary statistics"""
    if not os.path.exists(HISTORY_FILE):
        return {
            'total_checks': 0,
            'fake_detected': 0,
            'real_detected': 0,
            'today_checks': 0
        }
    
    df = pd.read_csv(HISTORY_FILE)
    df = df[df['is_deleted'] != True]
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    return {
        'total_checks': len(df),
        'fake_detected': len(df[df['prediction'] == 'FAKE']),
        'real_detected': len(df[df['prediction'] == 'REAL']),
        'today_checks': len(df[df['timestamp'].str.startswith(today)])
    }

def delete_history_item(item_id: str):
    """Soft delete a history item"""
    if not os.path.exists(HISTORY_FILE):
        return False
    
    df = pd.read_csv(HISTORY_FILE)
    df.loc[df['id'] == item_id, 'is_deleted'] = True
    df.to_csv(HISTORY_FILE, index=False)
    return True

def clear_all_history():
    """Clear all history"""
    init_history()
    return True