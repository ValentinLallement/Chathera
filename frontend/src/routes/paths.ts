export const PATHS = {
    home: '/',
    chat: '/chat',
    chatWithId: (id: string) => `/chat/${id}`,
    profile: '/profile',
    login: '/login',
    settings: '/settings',
  };

/**
 * <NavLink to={PATHS.chat}>Chat</NavLink>
 *
 * navigate(PATHS.chatWithId('42'));
 */