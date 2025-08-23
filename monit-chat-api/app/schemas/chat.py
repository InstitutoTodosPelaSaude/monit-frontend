from pydantic import BaseModel, Field
from typing import List

class TableColumnCreate(BaseModel):
    name: str = Field(..., description="Nome da coluna")
    type: str = Field(..., description="Tipo de dado da coluna, por exemplo: STRING, INTEGER")
    description: str = Field(..., description="Descrição do propósito ou conteúdo da coluna")

class TableMetadataCreate(BaseModel):
    name: str = Field(..., description="Nome técnico da tabela no banco")
    schema: str = Field(..., description="Schema ao qual a tabela pertence")
    database: str = Field(..., description="Banco de dados onde a tabela está armazenada")

class TableCreate(BaseModel):
    name: str = Field(..., description="Nome único da tabela")
    description: str = Field(..., description="Descrição geral da tabela e seu propósito")
    columns: List[TableColumnCreate] = Field(..., description="Lista de colunas que compõem a tabela")
    observations: str = Field(default="", description="Observações ou comentários adicionais sobre a tabela")

    metadata: TableMetadataCreate = Field(..., description="Metadados de schema e banco de dados da tabela")

class TableColumnUpdate(BaseModel):
    name: str = Field(..., description="Nome da coluna")
    description: str = Field(default=None, description="Descrição do propósito ou conteúdo da coluna")

class TableUpdate(BaseModel):
    name: str = Field(..., description="Nome único da tabela")
    description: str = Field(default=None, description="Descrição geral da tabela e seu propósito")
    observations: str = Field(default=None, description="Observações ou comentários adicionais sobre a tabela")
    columns: List[TableColumnUpdate] = Field(default_factory=list, description="Lista de colunas que compõem a tabela")

class ChatBasicIdentifiers(BaseModel):
    chat_id: str = Field(..., description="ID do chat")
    name: str = Field(..., description="Nome do chat")
