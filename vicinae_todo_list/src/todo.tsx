import React, { useEffect, useMemo, useState } from "react";
import {
  List,
  ActionPanel,
  Action,
  Icon,
  showToast,
  Toast,
  confirmAlert,
  getPreferenceValues,
  LocalStorage,
  useNavigation,
  Form,
  environment,
} from "@vicinae/api";

type Todo = {
  id: string;
  title: string;
  notes?: string;
  completed: boolean;
  createdAt: string;
};

const STORAGE_KEY = "vicinae.todolist.items.v1";

function uid() {
  return Math.random().toString(36).slice(2, 9);
}

function useTodos() {
  const [items, setItems] = useState<Todo[]>([]);
  const load = async () => {
    try {
      const raw = await LocalStorage.getItem<string>(STORAGE_KEY);
      if (raw) setItems(JSON.parse(raw));
    } catch (e) {
      // ignore
    }
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    // persist on change
    (async () => {
      try {
        await LocalStorage.setItem(STORAGE_KEY, JSON.stringify(items));
      } catch (e) {
        // ignore
      }
    })();
  }, [items]);

  const add = (title: string, notes?: string) => {
    const t: Todo = {
      id: uid(),
      title,
      notes,
      completed: false,
      createdAt: new Date().toISOString(),
    };
    setItems((s) => [t, ...s]);
    return t;
  };

  const toggle = (id: string) =>
    setItems((s) => s.map((it) => (it.id === id ? { ...it, completed: !it.completed } : it)));

  const remove = (id: string) => setItems((s) => s.filter((it) => it.id !== id));

  const clearCompleted = () => setItems((s) => s.filter((it) => !it.completed));

  return { items, add, toggle, remove, clearCompleted, reload: load };
}

function AddTodoForm({ onAdded }: { onAdded: (t: Todo) => void }) {
  const { push, pop } = useNavigation();
  return (
    <Form
      actions={
        <ActionPanel>
          <Action.SubmitForm
            title="Add Todo"
            onSubmit={(values) => {
              const title = String(values["title"] || "").trim();
              if (!title) return;
              const notes = values["notes"] ? String(values["notes"]) : undefined;
              // create a small object and navigate back using a pushed callback
              // We'll use showToast feedback and then pop the view
              const newTodo: Todo = {
                id: uid(),
                title,
                notes,
                completed: false,
                createdAt: new Date().toISOString(),
              };
              onAdded(newTodo);
              showToast(Toast.Style.Success, "Todo added", title);
              pop();
            }}
          />
        </ActionPanel>
      }
    >
      <Form.TextField id="title" title="Title" placeholder="What do you want to do?" autoFocus />
      <Form.TextArea id="notes" title="Notes" placeholder="Optional notes" />
    </Form>
  );
}

export default function TodoList() {
  const { items, add, toggle, remove, clearCompleted } = useTodos();
  const { push } = useNavigation();
  const active = useMemo(() => items.filter((i) => !i.completed), [items]);
  const completed = useMemo(() => items.filter((i) => i.completed), [items]);

  const handleAdd = () => {
    push(<AddTodoForm onAdded={(t) => add(t.title, t.notes)} />);
  };

  const handleClearCompleted = async () => {
    const ok = await confirmAlert({ title: "Remove completed todos?", message: "This will delete all completed todos.", primaryAction: { title: "Remove", style: "destructive" }, dismissAction: { title: "Cancel" } });
    if (ok) {
      clearCompleted();
      await showToast(Toast.Style.Success, "Cleared completed todos");
    }
  };

  return (
    <List
      isShowingDetail={true}
      searchBarPlaceholder={"Search todos..."}
      actions={
        <ActionPanel>
          <Action title="Add Todo" icon={Icon.Plus} onAction={handleAdd} />
          <Action title="Clear Completed" icon={Icon.Trash} style="destructive" onAction={handleClearCompleted} />
        </ActionPanel>
      }
    >
      <List.Section title={`Active (${active.length})`}>
        {active.map((t) => (
          <List.Item
            key={t.id}
            id={t.id}
            title={t.title}
            subtitle={t.notes}
            keywords={[...(t.notes ? [t.notes] : []), t.title]}
            icon={Icon.Circle}
            detail={<List.Item.Detail markdown={`**${t.title}**\n\n${t.notes || ""}`} />}
            actions={
              <ActionPanel>
                <Action title="Toggle Complete" icon={Icon.Check} onAction={() => toggle(t.id)} />
                <Action.CopyToClipboard title="Copy Title" content={t.title} />
                <Action
                  title="Delete"
                  icon={Icon.Trash}
                  style="destructive"
                  onAction={async () => {
                    const ok = await confirmAlert({ title: "Delete todo?", message: `Delete “${t.title}”?`, primaryAction: { title: "Delete", style: "destructive" }, dismissAction: { title: "Cancel" } });
                    if (ok) {
                      remove(t.id);
                      await showToast(Toast.Style.Success, "Todo deleted");
                    }
                  }}
                />
              </ActionPanel>
            }
          />
        ))}
      </List.Section>

      <List.Section title={`Completed (${completed.length})`}>
        {completed.map((t) => (
          <List.Item
            key={t.id}
            id={t.id}
            title={t.title}
            subtitle={t.notes}
            icon={Icon.CheckCircle}
            detail={<List.Item.Detail markdown={`**${t.title}**\n\n${t.notes || ""}`} />}
            actions={
              <ActionPanel>
                <Action title="Toggle Complete" icon={Icon.Circle} onAction={() => toggle(t.id)} />
                <Action.CopyToClipboard title="Copy Title" content={t.title} />
                <Action
                  title="Delete"
                  icon={Icon.Trash}
                  style="destructive"
                  onAction={async () => {
                    const ok = await confirmAlert({ title: "Delete todo?", message: `Delete “${t.title}”?`, primaryAction: { title: "Delete", style: "destructive" }, dismissAction: { title: "Cancel" } });
                    if (ok) {
                      remove(t.id);
                      await showToast(Toast.Style.Success, "Todo deleted");
                    }
                  }}
                />
              </ActionPanel>
            }
          />
        ))}
      </List.Section>

      {items.length === 0 && <List.EmptyView title="No todos" description="Press ⏎ to add a todo or use the Add action." icon={Icon.Clipboard} />}
    </List>
  );
}
