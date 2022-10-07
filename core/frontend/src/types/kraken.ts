import { Dictionary } from '@/types/common'

export interface Author {
    name: string
    email: string
}

export interface Company {
    logo: string
    name: string
    email: string
    about: string
}

export interface Version {
    permissions: any
    requirements: string | null
    tag: string
    authors?: Author[]
    docs?: string
    support?: string
    readme?: string
    website: string
    company?: Company
}

export interface ExtensionData {
    name: string
    description: string
    docker: string
    versions: Dictionary<Version>
    extension_logo?: string
}
