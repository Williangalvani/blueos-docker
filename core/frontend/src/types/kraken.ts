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
}

export interface ExtensionData {
    name: string
    description: string
    docker: string
    website: string
    versions: Dictionary<Version>
    authors?: Author[]
    readme?: string
    support?: string
    docs?: string
    extension_logo?: string
    company?: Company
}
