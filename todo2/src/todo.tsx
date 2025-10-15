import React, { useEffect, useState } from "react";
import {
  List,
  ActionPanel,
  Action,
  Icon,
  showToast,
  Toast,
  LocalStorage,
  Form,
  environment,
  useNavigation
} from "@vicinae/api";

type Todo = {
  id: string;
  title: string;
  completed: boolean;
  notes?: string;
};

const STORAGE_KEY = "vicinae-todo-items";

async function loadTodos(): Promise<Todo[]> {
  try {
    const raw = await LocalStorage.getItem<string>(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as Todo[];
  } catch (e) {
    return [];
  }
}

async function saveTodos(todos: Todo[]) {
  await LocalStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
}

function uid() {
  return Math.random().toString(36).slice(2, 9);
}

export default function TodoCommand() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [searchText, setSearchText] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const { push } = useNavigation();

  useEffect(() => {
    let mounted = true;
    (async () => {
      const items = await loadTodos();
      if (mounted) {
        setTodos(items);
        setIsLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    // persist on change
    saveTodos(todos).catch(() => {});
  }, [todos]);

  const addTodo = async (title: string, notes?: string) => {
    if (!title.trim()) return;
    const newTodo: Todo = { id: uid(), title: title.trim(), completed: false, notes };
    setTodos(prev => [newTodo, ...prev]);
    await showToast(Toast.Style.Success, "Todo added", title);
  };

  const toggle = async (id: string) => {
    setTodos(prev => prev.map(t => (t.id === id ? { ...t, completed: !t.completed } : t)));
  };

  const remove = async (id: string) => {
    setTodos(prev => prev.filter(t => t.id !== id));
    await showToast(Toast.Style.Success, "Todo removed");
  };

  const edit = (todo: Todo) => {
    push(<EditView todo={todo} onSave={async (updated) => {
      setTodos(prev => prev.map(t => (t.id === updated.id ? updated : t)));
    }} onDelete={async (id) => { await remove(id); }} />);
  };

  const filtered = todos.filter(t => t.title.toLowerCase().includes(searchText.toLowerCase()));

  return (
    <List
      isShowingDetail
      searchBarPlaceholder="Search todos..."
      onSearchTextChange={setSearchText}
      searchText={searchText}
      isLoading={isLoading}
      navigationTitle="Todos (Vicinae)"
    >
      <List.Section title="Add">
        <List.Item
          title="Add New Todo…"
          id="add-new"
          icon={Icon.Plus}
          actions={
            <ActionPanel>
              <Action.Push
                title="Add Todo"
                target={<AddView onAdd={async (title, notes) => { await addTodo(title, notes); }} />}
                icon={Icon.Plus}
              />
            </ActionPanel>
          }
        />
      </List.Section>

      <List.Section title={`Todos (${filtered.length})`}>
        {filtered.length === 0 && !isLoading ? (
          <List.EmptyView title="No todos" description="Add your first todo" />
        ) : null}

        {filtered.map(todo => (
          <List.Item
            key={todo.id}
            id={todo.id}
            title={todo.title}
            subtitle={todo.completed ? "Completed" : ""
            }
            icon={todo.completed ? Icon.CheckCircle : Icon.Circle}
            detail={<List.Item.Detail markdown={`${todo.notes ?? ""}`} />}
            actions={
              <ActionPanel>
                <Action
                  title={todo.completed ? "Mark as incomplete" : "Mark as complete"}
                  onAction={() => toggle(todo.id)}
                  icon={Icon.Check}
                />
                <Action
                  title="Edit"
                  onAction={() => edit(todo)}
                  icon={Icon.Pencil}
                />
                <Action
                  title="Delete"
                  onAction={async () => {
                    const confirmed = true;
                    if (confirmed) await remove(todo.id);
                  }}
                  icon={Icon.Trash}
                  style="destructive"
                />
              </ActionPanel>
            }
          />
        ))}
      </List.Section>

      <List.Section title="Tips">
        <List.Item title="Use Add to create new todos" icon={Icon.Info} />
      </List.Section>
    </List>
  );
}

function AddView({ onAdd }: { onAdd: (title: string, notes?: string) => Promise<void> }) {
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const { pop } = useNavigation();

  return (
    <Form
      actions={
        <ActionPanel>
          <Action.SubmitForm
            title="Add"
            onSubmit={async () => {
              if (!title.trim()) {
                await showToast(Toast.Style.Failure, "Title required");
                return false;
              }
              await onAdd(title, notes);
              pop();
            }}
          />
        </ActionPanel>
      }
    >
      <Form.TextField id="title" title="Title" value={title} onChange={setTitle} />
      <Form.TextArea id="notes" title="Notes" value={notes} onChange={setNotes} />
    </Form>
  );
}

function EditView({ todo, onSave, onDelete }: { todo: Todo; onSave: (t: Todo) => Promise<void>; onDelete: (id: string) => Promise<void> }) {
  const [title, setTitle] = useState(todo.title);
  const [notes, setNotes] = useState(todo.notes ?? "");
  const [completed, setCompleted] = useState(todo.completed);
  const { pop } = useNavigation();

  return (
    <Form
      actions={
        <ActionPanel>
          <Action.SubmitForm
            title="Save"
            onSubmit={async () => {
              if (!title.trim()) {
                await showToast(Toast.Style.Failure, "Title required");
                return false;
              }
              const updated: Todo = { ...todo, title: title.trim(), notes, completed };
              await onSave(updated);
              pop();
            }}
          />
          <Action
            title="Delete"
            onAction={async () => {
              await onDelete(todo.id);
              pop();
            }}
            style="destructive"
            icon={Icon.Trash}
          />
        </ActionPanel>
      }
    >
      <Form.TextField id="title" title="Title" value={title} onChange={setTitle} />
      <Form.TextArea id="notes" title="Notes" value={notes} onChange={setNotes} />
      <Form.Checkbox id="done" title="Completed" value={completed} onChange={setCompleted} />
    </Form>
  );
}
