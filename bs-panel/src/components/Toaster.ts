import { Position, Intent, OverlayToaster } from "@blueprintjs/core";

export const AppToaster = OverlayToaster.createAsync({
  className: "app-toaster",
  position: Position.TOP,
});

export const showToast = async (
  message: string,
  intent: Intent = Intent.PRIMARY
) => {
  (await AppToaster).show({ message, intent });
};
