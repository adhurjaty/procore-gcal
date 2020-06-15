export interface NamedItem {
    id: string,
    name: string
};

export interface UserItem extends NamedItem {
    email: string
}

export interface SelectableItem {
    name: string,
    enabled: boolean
};