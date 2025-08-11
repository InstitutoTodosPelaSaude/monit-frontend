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
    observations: List[str] = Field(default_factory=list, description="Observações ou comentários adicionais sobre a tabela")
    metadata: TableMetadataCreate = Field(..., description="Metadados de schema e banco de dados da tabela")
