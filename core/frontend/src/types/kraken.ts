export interface Author {
    name: string
    email: string
    about?: string
}

export interface ExtensionData {
    name: string
    description: string
    docker: string
    website: string
    permissions?: string
    requirements?: string
    tag?: string
    version?: string
    authors?: Author[]
    readme?: string
    support?: string
    docs?: string
}
