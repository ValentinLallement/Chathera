export interface Message {
    content: string;
    user_id: string;
    conversation_id: string;
    id: string;
    created_at: string;
}

export interface Conversation {
    messages: Message[];
}