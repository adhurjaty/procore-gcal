export interface NamedItem {
    id: number,
    name: string
};

export interface UserItem extends NamedItem {
    email: string
}

export interface SelectableItem extends NamedItem {
    enabled: boolean
};